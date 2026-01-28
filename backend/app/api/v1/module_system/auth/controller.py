from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import ErrorResponse, SuccessResponse
from app.config.setting import settings
from app.core.dependencies import db_getter, get_current_user, redis_getter
from app.core.logger import log
from app.core.router_class import OperationLogRoute
from app.core.security import CustomOAuth2PasswordRequestForm

from .schema import (
    CaptchaOutSchema,
    JWTOutSchema,
    LogoutPayloadSchema,
    RefreshTokenPayloadSchema,
    WechatAuthorizeRequestSchema,
    WechatCallbackRequestSchema,
    WechatQRCodeSchema,
    WechatLoginSchema,
)
from .service import CaptchaService, LoginService, WechatOAuthService

AuthRouter = APIRouter(route_class=OperationLogRoute, prefix="/auth", tags=["认证授权"])


@AuthRouter.post("/login", summary="登录", description="登录", response_model=JWTOutSchema)
async def login_for_access_token_controller(
    request: Request,
    redis: Annotated[Redis, Depends(redis_getter)],
    login_form: Annotated[CustomOAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(db_getter)],
) -> JSONResponse | dict:
    """
    用户登录

    参数:
    - request (Request): FastAPI请求对象
    - login_form (CustomOAuth2PasswordRequestForm): 登录表单数据
    - db (AsyncSession): 数据库会话对象

    返回:
    - JWTOutSchema: 包含访问令牌和刷新令牌的响应模型

    异常:
    - CustomException: 认证失败时抛出异常。
    """
    login_token = await LoginService.authenticate_user_service(request=request, redis=redis, login_form=login_form, db=db)

    log.info(f"用户{login_form.username}登录成功")

    # 如果是文档请求，则不记录日志:http://localhost:8000/api/v1/docs
    if settings.DOCS_URL in request.headers.get("referer", ""):
        return login_token.model_dump()
    return SuccessResponse(data=login_token.model_dump(), msg="登录成功")


@AuthRouter.post("/token/refresh", summary="刷新token", description="刷新token", response_model=JWTOutSchema, dependencies=[Depends(get_current_user)])
async def get_new_token_controller(
    request: Request,
    payload: RefreshTokenPayloadSchema,
    db: Annotated[AsyncSession, Depends(db_getter)],
    redis: Annotated[Redis, Depends(redis_getter)]
) -> JSONResponse:
    """
    刷新token

    参数:
    - request (Request): FastAPI请求对象
    - payload (RefreshTokenPayloadSchema): 刷新令牌负载模型

    返回:
    - JWTOutSchema: 包含新的访问令牌和刷新令牌的响应模型

    异常:
    - CustomException: 刷新令牌失败时抛出异常。
    """
    # 解析当前的访问Token以获取用户名
    new_token = await LoginService.refresh_token_service(db=db, request=request, redis=redis, refresh_token=payload)
    token_dict = new_token.model_dump()
    log.info(f"刷新token成功: {token_dict}")
    return SuccessResponse(data=token_dict, msg="刷新成功")


@AuthRouter.get("/captcha/get", summary="获取验证码", description="获取登录验证码", response_model=CaptchaOutSchema)
async def get_captcha_for_login_controller(
    redis: Annotated[Redis, Depends(redis_getter)]
) -> JSONResponse:
    """
    获取登录验证码

    参数:
    - redis (Redis): Redis客户端对象

    返回:
    - CaptchaOutSchema: 包含验证码图片和key的响应模型

    异常:
    - CustomException: 获取验证码失败时抛出异常。
    """
    # 获取验证码
    captcha = await CaptchaService.get_captcha_service(redis=redis)
    log.info("获取验证码成功")
    return SuccessResponse(data=captcha, msg="获取验证码成功")


@AuthRouter.post('/logout', summary="退出登录", description="退出登录", dependencies=[Depends(get_current_user)])
async def logout_controller(
    payload: LogoutPayloadSchema,
    redis: Annotated[Redis, Depends(redis_getter)]
) -> JSONResponse:
    """
    退出登录

    参数:
    - payload (LogoutPayloadSchema): 退出登录负载模型
    - redis (Redis): Redis客户端对象

    返回:
    - JSONResponse: 包含退出登录结果的响应模型

    异常:
    - CustomException: 退出登录失败时抛出异常。
    """
    if await LoginService.logout_service(redis=redis, token=payload):
        log.info('退出成功')
        return SuccessResponse(msg='退出成功')
    return ErrorResponse(msg='退出失败')


@AuthRouter.post("/wechat/authorize", summary="微信扫码登录授权", description="获取微信扫码登录二维码", response_model=WechatQRCodeSchema)
async def wechat_authorize_controller(
    request_data: WechatAuthorizeRequestSchema
) -> JSONResponse:
    """
    微信扫码登录授权

    参数:
    - request_data (WechatAuthorizeRequestSchema): 微信授权请求模型

    返回:
    - WechatQRCodeSchema: 包含二维码URL和状态码的响应模型

    异常:
    - CustomException: 微信OAuth未启用时抛出异常。
    """
    qr_code_info = WechatOAuthService.get_wechat_qr_code_service(request_data=request_data)
    log.info('获取微信二维码成功')
    return SuccessResponse(data=qr_code_info.model_dump(), msg='获取微信二维码成功')


@AuthRouter.post("/wechat/callback", summary="微信OAuth回调", description="微信OAuth回调处理", dependencies=[Depends(get_current_user)])
async def wechat_callback_controller(
    request: Request,
    redis: Annotated[Redis, Depends(redis_getter)],
    db: Annotated[AsyncSession, Depends(db_getter)],
    callback_data: WechatCallbackRequestSchema
) -> JSONResponse:
    """
    微信OAuth回调处理

    参数:
    - request (Request): FastAPI请求对象
    - redis (Redis): Redis客户端对象
    - db (AsyncSession): 数据库会话对象
    - callback_data (WechatCallbackRequestSchema): 微信回调数据模型

    返回:
    - JSONResponse: 包含access_token和用户信息的响应模型

    异常:
    - CustomException: 回调处理失败时抛出异常。
    """
    # 通过授权码获取access_token
    token_info = await WechatOAuthService.get_wechat_access_token_service(code=callback_data.code)
    access_token = token_info.get('access_token')
    openid = token_info.get('openid')

    # 获取微信用户信息
    user_info = await WechatOAuthService.get_wechat_user_info_service(access_token=access_token, openid=openid)

    # 执行微信登录
    login_token = await WechatOAuthService.wechat_login_service(
        request=request,
        redis=redis,
        db=db,
        login_data=WechatLoginSchema(
            openid=openid,
            unionid=user_info.unionid,
            nickname=user_info.nickname,
            headimgurl=user_info.headimgurl,
            login_type="微信登录"
        )
    )

    log.info(f"微信登录成功,openid:{openid},昵称:{user_info.nickname}")

    return SuccessResponse(data={
        'token': login_token.model_dump(),
        'user_info': user_info.model_dump()
    }, msg='微信登录成功')
