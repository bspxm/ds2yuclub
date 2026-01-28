import json
import uuid

from datetime import datetime, timedelta
from typing import NewType

from fastapi import Request
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from user_agents import parse

from app.api.v1.module_monitor.online.schema import OnlineOutSchema
from app.api.v1.module_system.user.crud import UserCRUD
from app.api.v1.module_system.user.model import UserModel
from app.common.enums import RedisInitKeyConfig
from app.config.setting import settings
from app.core.exceptions import CustomException
from app.core.logger import log
from app.core.redis_crud import RedisCURD
from app.core.security import CustomOAuth2PasswordRequestForm, create_access_token, decode_access_token
from app.utils.captcha_util import CaptchaUtil
from app.utils.common_util import get_random_character
from app.utils.hash_bcrpy_util import PwdUtil
from app.utils.ip_local_util import IpLocalUtil

from .schema import (
    AuthSchema,
    CaptchaOutSchema,
    JWTOutSchema,
    JWTPayloadSchema,
    LogoutPayloadSchema,
    RefreshTokenPayloadSchema,
    WechatAuthorizeRequestSchema,
    WechatCallbackRequestSchema,
    WechatQRCodeSchema,
    WechatUserInfoSchema,
    WechatLoginSchema,
)

CaptchaKey = NewType('CaptchaKey', str)
CaptchaBase64 = NewType('CaptchaBase64', str)


class LoginService:
    """登录认证服务"""

    @classmethod
    async def authenticate_user_service(cls, request: Request, redis: Redis, login_form: CustomOAuth2PasswordRequestForm, db: AsyncSession) -> JWTOutSchema:
        """
        用户认证

        参数:
        - request (Request): FastAPI请求对象
        - login_form (CustomOAuth2PasswordRequestForm): 登录表单数据
        - db (AsyncSession): 数据库会话对象

        返回:
        - JWTOutSchema: 包含访问令牌和刷新令牌的响应模型

        异常:
        - CustomException: 认证失败时抛出异常。
        """
        # 判断是否来自API文档
        referer = request.headers.get('referer', '')
        request_from_docs = referer.endswith(('docs', 'redoc'))

        # 验证码校验
        if settings.CAPTCHA_ENABLE and not request_from_docs:
            if not login_form.captcha_key or not login_form.captcha:
                raise CustomException(msg="验证码不能为空")
            await CaptchaService.check_captcha_service(redis=redis, key=login_form.captcha_key, captcha=login_form.captcha)

        # 用户认证
        auth = AuthSchema(db=db)
        # 首先尝试通过用户名查找用户
        user = await UserCRUD(auth).get_by_username_crud(username=login_form.username)
        
        # 如果通过用户名找不到，尝试通过手机号查找
        if not user:
            user = await UserCRUD(auth).get_by_mobile_crud(mobile=login_form.username)
        
        if not user:
            raise CustomException(msg="用户不存在")

        if not PwdUtil.verify_password(plain_password=login_form.password, password_hash=user.password):
            raise CustomException(msg="账号或密码错误")

        if user.status == "1":
            raise CustomException(msg="用户已被停用")

        # 更新最后登录时间
        user = await UserCRUD(auth).update_last_login_crud(id=user.id)
        if not user:
            raise CustomException(msg="用户不存在")
        if not login_form.login_type:
            raise CustomException(msg="登录类型不能为空")

        # 创建token
        token = await cls.create_token_service(request=request, redis=redis, user=user, login_type=login_form.login_type)

        return token

    @classmethod
    async def create_token_service(cls, request: Request, redis: Redis, user: UserModel, login_type: str) -> JWTOutSchema:
        """
        创建访问令牌和刷新令牌

        参数:
        - request (Request): FastAPI请求对象
        - redis (Redis): Redis客户端对象
        - user (UserModel): 用户模型对象
        - login_type (str): 登录类型

        返回:
        - JWTOutSchema: 包含访问令牌和刷新令牌的响应模型

        异常:
        - CustomException: 创建令牌失败时抛出异常。
        """
        # 生成会话编号
        session_id = str(uuid.uuid4())
        request.scope["session_id"] = session_id

        user_agent = parse(request.headers.get("user-agent"))
        request_ip = None
        x_forwarded_for = request.headers.get('X-Forwarded-For')
        if x_forwarded_for:
            # 取第一个 IP 地址，通常为客户端真实 IP
            request_ip = x_forwarded_for.split(',')[0].strip()
        else:
            # 若没有 X-Forwarded-For 头，则使用 request.client.host
            request_ip = request.client.host if request.client else "127.0.0.1"

        login_location = await IpLocalUtil.get_ip_location(request_ip)
        request.scope["login_location"] = login_location

        # 确保在请求上下文中设置用户名和会话ID
        request.scope["user_username"] = user.username

        access_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

        now = datetime.now()

        # 记录租户信息到日志
        log.info(f"用户ID: {user.id}, 用户名: {user.username} 正在生成JWT令牌")

        # 生成会话信息
        session_info = OnlineOutSchema(
            session_id=session_id,
            user_id=user.id,
            name=user.name,
            user_name=user.username,
            ipaddr=request_ip,
            login_location=login_location,
            os=user_agent.os.family,
            browser=user_agent.browser.family,
            login_time=user.last_login,
            login_type=login_type
        ).model_dump_json()

        access_token = create_access_token(payload=JWTPayloadSchema(
            sub=session_info,
            is_refresh=False,
            exp=now + access_expires,
        ))
        refresh_token = create_access_token(payload=JWTPayloadSchema(
            sub=session_info,
            is_refresh=True,
            exp=now + refresh_expires,
        ))

        # 设置新的token
        await RedisCURD(redis).set(
            key=f'{RedisInitKeyConfig.ACCESS_TOKEN.key}:{session_id}',
            value=access_token,
            expire=int(access_expires.total_seconds())
        )

        await RedisCURD(redis).set(
            key=f'{RedisInitKeyConfig.REFRESH_TOKEN.key}:{session_id}',
            value=refresh_token,
            expire=int(refresh_expires.total_seconds())
        )

        return JWTOutSchema(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(access_expires.total_seconds()),
            token_type=settings.TOKEN_TYPE
        )

    @classmethod
    async def refresh_token_service(cls, db: AsyncSession, redis: Redis, request: Request, refresh_token: RefreshTokenPayloadSchema) -> JWTOutSchema:
        """
        刷新访问令牌

        参数:
        - db (AsyncSession): 数据库会话对象
        - redis (Redis): Redis客户端对象
        - request (Request): FastAPI请求对象
        - refresh_token (RefreshTokenPayloadSchema): 刷新令牌数据

        返回:
        - JWTOutSchema: 新的令牌对象

        异常:
        - CustomException: 刷新令牌无效时抛出异常
        """
        token_payload: JWTPayloadSchema = decode_access_token(token=refresh_token.refresh_token)
        if not token_payload.is_refresh:
            raise CustomException(msg="非法凭证，请传入刷新令牌")

        # 去 Redis 查完整信息
        session_info = json.loads(token_payload.sub)
        session_id = session_info.get("session_id")
        user_id = session_info.get("user_id")

        if not session_id or not user_id:
            raise CustomException(msg="非法凭证,无法获取会话编号或用户ID")

        # 用户认证
        auth = AuthSchema(db=db)
        user = await UserCRUD(auth).get_by_id_crud(id=user_id)
        if not user:
            raise CustomException(msg="刷新token失败，用户不存在")

        # 记录刷新令牌时的租户信息
        log.info(f"用户ID: {user.id}, 用户名: {user.username} 正在刷新JWT令牌")

        # 设置新的 token
        access_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        now = datetime.now()

        session_info_json = json.dumps(session_info)

        access_token = create_access_token(payload=JWTPayloadSchema(
            sub=session_info_json,
            is_refresh=False,
            exp=now + access_expires
        ))

        refresh_token_new = create_access_token(payload=JWTPayloadSchema(
            sub=session_info_json,
            is_refresh=True,
            exp=now + refresh_expires
        ))

        # 覆盖写入 Redis
        await RedisCURD(redis).set(
            key=f'{RedisInitKeyConfig.ACCESS_TOKEN.key}:{session_id}',
            value=access_token,
            expire=int(access_expires.total_seconds())
        )

        await RedisCURD(redis).set(
            key=f'{RedisInitKeyConfig.REFRESH_TOKEN.key}:{session_id}',
            value=refresh_token_new,
            expire=int(refresh_expires.total_seconds())
        )

        return JWTOutSchema(
            access_token=access_token,
            refresh_token=refresh_token_new,
            token_type=settings.TOKEN_TYPE,
            expires_in=int(access_expires.total_seconds())
        )

    @classmethod
    async def logout_service(cls, redis: Redis, token: LogoutPayloadSchema) -> bool:
        """
        退出登录

        参数:
        - redis (Redis): Redis客户端对象
        - token (LogoutPayloadSchema): 退出登录令牌数据

        返回:
        - bool: 退出成功返回True

        异常:
        - CustomException: 令牌无效时抛出异常
        """
        payload: JWTPayloadSchema = decode_access_token(token=token.token)
        session_info = json.loads(payload.sub)
        session_id = session_info.get("session_id")

        if not session_id:
            raise CustomException(msg="非法凭证,无法获取会话编号")

        # 删除Redis中的在线用户、访问令牌、刷新令牌
        await RedisCURD(redis).delete(f"{RedisInitKeyConfig.ACCESS_TOKEN.key}:{session_id}")
        await RedisCURD(redis).delete(f"{RedisInitKeyConfig.REFRESH_TOKEN.key}:{session_id}")

        log.info(f"用户退出登录成功,会话编号:{session_id}")

        return True


class CaptchaService:
    """验证码服务"""

    @classmethod
    async def get_captcha_service(cls, redis: Redis) -> dict[str, CaptchaKey | CaptchaBase64]:
        """
        获取验证码

        参数:
        - redis (Redis): Redis客户端对象

        返回:
        - dict[str, CaptchaKey | CaptchaBase64]: 包含验证码key和base64图片的字典

        异常:
        - CustomException: 验证码服务未启用时抛出异常
        """
        if not settings.CAPTCHA_ENABLE:
            raise CustomException(msg="未开启验证码服务")

        # 生成验证码图片和值
        captcha_base64, captcha_value = CaptchaUtil.captcha_arithmetic()
        captcha_key = get_random_character()

        # 保存到Redis并设置过期时间
        redis_key = f"{RedisInitKeyConfig.CAPTCHA_CODES.key}:{captcha_key}"
        await RedisCURD(redis).set(
            key=redis_key,
            value=captcha_value,
            expire=settings.CAPTCHA_EXPIRE_SECONDS
        )

        log.info(f"生成验证码成功,验证码:{captcha_value}")

        # 返回验证码信息
        return CaptchaOutSchema(
            enable=settings.CAPTCHA_ENABLE,
            key=CaptchaKey(captcha_key),
            img_base=CaptchaBase64(f"data:image/png;base64,{captcha_base64}")
        ).model_dump()

    @classmethod
    async def check_captcha_service(cls, redis: Redis, key: str, captcha: str) -> bool:
        """
        校验验证码

        参数:
        - redis (Redis): Redis客户端对象
        - key (str): 验证码key
        - captcha (str): 用户输入的验证码

        返回:
        - bool: 验证通过返回True

        异常:
        - CustomException: 验证码无效或错误时抛出异常
        """
        if not captcha:
            raise CustomException(msg="验证码不能为空")

        # 获取Redis中存储的验证码
        redis_key = f'{RedisInitKeyConfig.CAPTCHA_CODES.key}:{key}'

        captcha_value = await RedisCURD(redis).get(redis_key)
        if not captcha_value:
            log.error('验证码已过期或不存在')
            raise CustomException(msg="验证码已过期")

        # 验证码不区分大小写比对
        if captcha.lower() != captcha_value.lower():
            log.error(f'验证码错误,用户输入:{captcha},正确值:{captcha_value}')
            raise CustomException(msg="验证码错误")

        # 验证成功后删除验证码,避免重复使用
        await RedisCURD(redis).delete(redis_key)
        log.info(f'验证码校验成功,key:{key}')
        return True


class WechatOAuthService:
    """微信OAuth服务"""

    @classmethod
    def get_wechat_qr_code_service(cls, request_data: WechatAuthorizeRequestSchema) -> WechatQRCodeSchema:
        """
        生成微信扫码登录二维码

        参数:
        - request_data (WechatAuthorizeRequestSchema): 微信授权请求模型

        返回:
        - WechatQRCodeSchema: 包含二维码URL和状态码的响应模型

        异常:
        - CustomException: 微信OAuth未启用时抛出异常
        """
        if not settings.WECHAT_OAUTH_ENABLE:
            raise CustomException(msg="未启用微信OAuth登录")

        # 微信扫码登录授权URL
        qr_code_url = (
            f"https://open.weixin.qq.com/connect/qrconnect"
            f"?appid={settings.WECHAT_APPID}"
            f"&redirect_uri={settings.WECHAT_REDIRECT_URI}"
            f"&response_type=code"
            f"&scope=snsapi_login"
            f"&state={request_data.state}#wechat_redirect"
        )

        log.info(f"生成微信二维码成功,state:{request_data.state}")

        return WechatQRCodeSchema(
            qr_code_url=qr_code_url,
            state=request_data.state,
            expires_in=120  # 二维码有效期2分钟
        )

    @classmethod
    async def get_wechat_access_token_service(cls, code: str) -> dict:
        """
        通过微信授权码获取access_token

        参数:
        - code (str): 微信授权码

        返回:
        - dict: 包含access_token、openid等信息的字典

        异常:
        - CustomException: 获取access_token失败时抛出异常
        """
        if not settings.WECHAT_OAUTH_ENABLE:
            raise CustomException(msg="未启用微信OAuth登录")

        # 微信OAuth获取access_token的API地址
        token_url = (
            f"https://api.weixin.qq.com/sns/oauth2/access_token"
            f"?appid={settings.WECHAT_APPID}"
            f"&secret={settings.WECHAT_APPSECRET}"
            f"&code={code}"
            f"&grant_type=authorization_code"
        )

        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(token_url)
            result = response.json()

        if 'errcode' in result:
            error_msg = result.get('errmsg', '未知错误')
            log.error(f"获取微信access_token失败,errcode:{result.get('errcode')},errmsg:{error_msg}")
            raise CustomException(msg=f"获取微信access_token失败:{error_msg}")

        log.info(f"获取微信access_token成功,openid:{result.get('openid')}")
        return result

    @classmethod
    async def get_wechat_user_info_service(cls, access_token: str, openid: str) -> WechatUserInfoSchema:
        """
        获取微信用户信息

        参数:
        - access_token (str): 微信access_token
        - openid (str): 微信openid

        返回:
        - WechatUserInfoSchema: 微信用户信息模型

        异常:
        - CustomException: 获取用户信息失败时抛出异常
        """
        if not settings.WECHAT_OAUTH_ENABLE:
            raise CustomException(msg="未启用微信OAuth登录")

        # 微信获取用户信息的API地址
        user_info_url = (
            f"https://api.weixin.qq.com/sns/userinfo"
            f"?access_token={access_token}"
            f"&openid={openid}"
            "&lang=zh_CN"
        )

        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(user_info_url)
            result = response.json()

        if 'errcode' in result:
            error_msg = result.get('errmsg', '未知错误')
            log.error(f"获取微信用户信息失败,errcode:{result.get('errcode')},errmsg:{error_msg}")
            raise CustomException(msg=f"获取微信用户信息失败:{error_msg}")

        user_info = WechatUserInfoSchema(
            openid=result.get('openid'),
            nickname=result.get('nickname'),
            headimgurl=result.get('headimgurl'),
            sex=result.get('sex'),
            province=result.get('province'),
            city=result.get('city'),
            country=result.get('country'),
            unionid=result.get('unionid')
        )

        log.info(f"获取微信用户信息成功,openid:{user_info.openid},nickname:{user_info.nickname}")
        return user_info

    @classmethod
    async def wechat_login_service(cls, request: Request, redis: Redis, db: AsyncSession, login_data: WechatLoginSchema) -> JWTOutSchema:
        """
        微信登录服务

        参数:
        - request (Request): FastAPI请求对象
        - redis (Redis): Redis客户端对象
        - db (AsyncSession): 数据库会话对象
        - login_data (WechatLoginSchema): 微信登录数据模型

        返回:
        - JWTOutSchema: 包含访问令牌和刷新令牌的响应模型

        异常:
        - CustomException: 登录失败时抛出异常
        """
        if not settings.WECHAT_OAUTH_ENABLE:
            raise CustomException(msg="未启用微信OAuth登录")

        # 用户认证
        auth = AuthSchema(db=db)

        # 检查用户是否已存在（通过wx_login字段）
        user = await UserCRUD(auth).get_by_wx_login_crud(wx_login=login_data.openid)

        if user:
            # 用户已存在，直接登录
            log.info(f"微信用户已存在,openid:{login_data.openid},用户名:{user.username}")
        else:
            # 用户不存在，自动注册
            log.info(f"微信用户不存在,自动注册,openid:{login_data.openid},昵称:{login_data.nickname}")

            # 生成用户名（使用微信openid）
            username = f"wx_{login_data.openid}"

            # 检查用户名是否已存在
            existing_user = await UserCRUD(auth).get_by_username_crud(username=username)
            if existing_user:
                username = f"wx_{login_data.openid}_{get_random_character()}"

            # 默认密码（随机生成）
            default_password = get_random_character(16)

            # 创建新用户
            user = await UserCRUD(auth).create_crud({
                'username': username,
                'password': PwdUtil.hash_password(default_password),
                'name': login_data.nickname or '微信用户',
                'mobile': None,  # 微信扫码登录时手机号可能为空
                'avatar': login_data.headimgurl,
                'wx_login': login_data.openid,
                'status': '0',  # 启用状态
                'is_superuser': False,
                'gender': str(login_data.sex) if login_data.sex else '2'
            })

            if not user:
                raise CustomException(msg="微信用户注册失败")

            # 分配家长角色
            await cls.assign_parent_role_service(db=db, user_id=user.id)

            log.info(f"微信用户注册成功,用户名:{user.username},openid:{login_data.openid}")

        # 更新最后登录时间
        user = await UserCRUD(auth).update_last_login_crud(id=user.id)
        if not user:
            raise CustomException(msg="用户不存在")

        # 创建token
        token = await LoginService.create_token_service(request=request, redis=redis, user=user, login_type=login_data.login_type)

        return token

    @classmethod
    async def assign_parent_role_service(cls, db: AsyncSession, user_id: int) -> bool:
        """
        为用户分配家长角色

        参数:
        - db (AsyncSession): 数据库会话对象
        - user_id (int): 用户ID

        返回:
        - bool: 分配成功返回True

        异常:
        - CustomException: 分配角色失败时抛出异常
        """
        from app.api.v1.module_system.role.crud import RoleCRUD

        auth = AuthSchema(db=db)

        # 查找家长角色
        parent_role = await RoleCRUD(auth).get_by_code_crud(code='parent')
        if not parent_role:
            log.warning("未找到家长角色，跳过角色分配")
            return False

        # 为用户分配家长角色
        await UserCRUD(auth).assign_role_crud(user_id=user_id, role_id=parent_role.id)

        log.info(f"为用户{user_id}分配家长角色成功")
        return True
