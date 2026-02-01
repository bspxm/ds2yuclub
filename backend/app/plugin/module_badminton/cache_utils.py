"""
羽毛球业务模块 - Redis缓存工具
提供常用的缓存操作函数
"""
import hashlib
import json
from datetime import date
from functools import lru_cache
from typing import Any, Optional

from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.core.redis_crud import RedisCURD


class BadmintonCacheKeys:
    """缓存键名常量"""
    # 时间段字典缓存
    TIME_SLOT_DICT = "badminton:time_slot_dict"
    
    # 班级相关缓存
    CLASS_TIME_SLOTS = "badminton:class_time_slots"
    CLASS_DETAIL = "badminton:class_detail"
    
    # 学员相关缓存
    STUDENT_DETAIL = "badminton:student_detail"
    STUDENT_SESSIONS = "badminton:student_sessions"
    
    # 可用学员列表缓存
    AVAILABLE_STUDENTS = "badminton:available_students"
    
    # 排课记录缓存
    SCHEDULES = "badminton:schedules"
    CLASS_SCHEDULE_DETAIL = "badminton:class_schedule_detail"
    
    # 学期班级列表缓存
    SEMESTER_CLASSES = "badminton:semester_classes"


class BadmintonCache:
    """羽毛球业务缓存工具类"""
    
    @staticmethod
    def hash_dict(data: dict) -> str:
        """将字典转换为哈希字符串，用于缓存键"""
        sorted_items = sorted(data.items())
        json_str = json.dumps(sorted_items, ensure_ascii=False)
        return hashlib.md5(json_str.encode()).hexdigest()
    
    @staticmethod
    async def get_json(redis: Redis, key: str) -> Optional[dict]:
        """从Redis获取JSON数据"""
        try:
            redis_crud = RedisCURD(redis)
            data = await redis_crud.get(key)
            if data is None:
                return None

            # 如果是bytes类型，先解码为字符串
            if isinstance(data, bytes):
                data = data.decode('utf-8')

            # 如果是字符串，尝试解析为JSON
            if isinstance(data, str):
                try:
                    return json.loads(data)
                except json.JSONDecodeError:
                    logger.warning(f"缓存数据不是有效的JSON: key={key}, data={data[:100]}")
                    return None

            # 其他类型（如整数）直接返回
            return data
        except Exception as e:
            logger.error(f"获取缓存失败: key={key}, error={e}")
            return None
    
    @staticmethod
    async def set_json(redis: Redis, key: str, data: Any, expire: int = None) -> bool:
        """将JSON数据存入Redis"""
        try:
            redis_crud = RedisCURD(redis)
            json_data = json.dumps(data, ensure_ascii=False)
            return await redis_crud.set(key, json_data, expire)
        except Exception as e:
            logger.error(f"设置缓存失败: key={key}, error={e}")
            return False
    
    @staticmethod
    async def delete_pattern(redis: Redis, pattern: str) -> bool:
        """删除匹配模式的缓存键"""
        try:
            redis_crud = RedisCURD(redis)
            keys = await redis_crud.get_keys(pattern)
            if keys:
                return await redis_crud.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"删除缓存失败: pattern={pattern}, error={e}")
            return False


# ============================================================================
# 缓存过期时间配置（单位：秒）
# ============================================================================
class CacheExpireTime:
    """缓存过期时间配置"""
    TIME_SLOT_DICT = 7200       # 时间段字典: 2小时
    CLASS_TIME_SLOTS = 1800     # 班级时间段: 30分钟
    AVAILABLE_STUDENTS = 600    # 可用学员列表: 10分钟
    STUDENT_SESSIONS = 60       # 学员剩余课时: 1分钟（需要实时性）
    SEMESTER_CLASSES = 3600     # 学期班级列表: 1小时
    CLASS_DETAIL = 1800         # 班级详情: 30分钟
    STUDENT_DETAIL = 1800       # 学员详情: 30分钟
    SCHEDULES = 300             # 排课记录: 5分钟


# ============================================================================
# 本地缓存装饰器
# ============================================================================
from app.api.v1.module_system.dict.service import DictDataService

# 使用 lru_cache 缓存时间段字典（本地缓存，无需Redis）
@lru_cache(maxsize=10)
def get_time_slot_dict_cached(dict_type: str) -> str:
    """
    获取时间段字典的本地缓存版本
    注意：这个函数返回JSON字符串，需要在调用后手动加载
    
    参数:
        dict_type: 字典类型（如 'badminton_time_slot'）
    
    返回:
        str: JSON字符串
    """
    return ""


async def get_time_slot_dict_with_cache(redis: Redis, dict_type: str = 'badminton_time_slot') -> list[dict]:
    """
    获取时间段字典（使用多层缓存：Redis + lru_cache）
    
    参数:
        redis: Redis客户端
        dict_type: 字典类型
    
    返回:
        list[dict]: 时间段字典数据
    """
    cache_key = BadmintonCacheKeys.TIME_SLOT_DICT

    # 1. 尝试从Redis获取
    redis_crud = RedisCURD(redis)
    cached_data = await redis_crud.get(cache_key)
    if cached_data is not None:
        try:
            # 如果是bytes类型，先解码
            if isinstance(cached_data, bytes):
                cached_data = cached_data.decode('utf-8')
            # 如果是字符串，尝试解析为JSON
            if isinstance(cached_data, str):
                return json.loads(cached_data)
            # 其他类型直接返回
            return cached_data
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"缓存数据解析失败: key={cache_key}, error={e}")
            pass
    
    # 2. 从数据库获取
    time_slot_data = await DictDataService.get_init_dict_service(redis, dict_type)
    
    # 3. 存入Redis缓存
    await redis_crud.set(cache_key, json.dumps(time_slot_data, ensure_ascii=False), CacheExpireTime.TIME_SLOT_DICT)
    
    return time_slot_data


async def invalidate_time_slot_cache(redis: Redis) -> bool:
    """失效时间段字典缓存"""
    cache_key = BadmintonCacheKeys.TIME_SLOT_DICT
    redis_crud = RedisCURD(redis)
    return await redis_crud.delete(cache_key)


class BadmintonCacheInvalidator:
    """羽毛球业务缓存失效工具类"""

    @staticmethod
    async def invalidate_student_sessions(redis: Redis, student_id: int, class_id: int) -> bool:
        """失效学员课时缓存"""
        cache_key = f"{BadmintonCacheKeys.STUDENT_SESSIONS}:{student_id}:{class_id}"
        return await BadmintonCache.delete_pattern(redis, cache_key)

    @staticmethod
    async def invalidate_student_all_sessions(redis: Redis, student_id: int) -> bool:
        """失效学员所有班级的课时缓存"""
        cache_pattern = f"{BadmintonCacheKeys.STUDENT_SESSIONS}:{student_id}:*"
        return await BadmintonCache.delete_pattern(redis, cache_pattern)

    @staticmethod
    async def invalidate_class_time_slots(redis: Redis, class_id: int, day_of_week: int = None) -> bool:
        """失效班级可用时间段缓存"""
        cache_key = f"{BadmintonCacheKeys.CLASS_TIME_SLOTS}:{class_id}"
        if day_of_week is not None:
            cache_key += f":{day_of_week}"
        redis_crud = RedisCURD(redis)
        return await redis_crud.delete(cache_key)

    @staticmethod
    async def invalidate_class_detail(redis: Redis, class_id: int) -> bool:
        """失效班级详情缓存"""
        cache_key = f"{BadmintonCacheKeys.CLASS_DETAIL}:{class_id}"
        redis_crud = RedisCURD(redis)
        return await redis_crud.delete(cache_key)

    @staticmethod
    async def invalidate_student_detail(redis: Redis, student_id: int) -> bool:
        """失效学员详情缓存"""
        cache_key = f"{BadmintonCacheKeys.STUDENT_DETAIL}:{student_id}"
        redis_crud = RedisCURD(redis)
        return await redis_crud.delete(cache_key)

    @staticmethod
    async def invalidate_available_students(redis: Redis, semester_id: int, schedule_date: date = None) -> bool:
        """失效可用学员列表缓存（可按学期和日期失效）"""
        if schedule_date:
            cache_pattern = f"{BadmintonCacheKeys.AVAILABLE_STUDENTS}:{semester_id}:{schedule_date}:*"
        else:
            cache_pattern = f"{BadmintonCacheKeys.AVAILABLE_STUDENTS}:{semester_id}:*"
        return await BadmintonCache.delete_pattern(redis, cache_pattern)

    @staticmethod
    async def invalidate_semester_classes(redis: Redis, semester_id: int) -> bool:
        """失效学期班级列表缓存"""
        cache_key = f"{BadmintonCacheKeys.SEMESTER_CLASSES}:{semester_id}"
        redis_crud = RedisCURD(redis)
        return await redis_crud.delete(cache_key)

    @staticmethod
    async def invalidate_all_student_related(redis: Redis, student_id: int) -> bool:
        """失效学员相关的所有缓存"""
        success = True
        try:
            # 失效学员详情
            await BadmintonCacheInvalidator.invalidate_student_detail(redis, student_id)
            # 失效学员所有课时缓存
            await BadmintonCacheInvalidator.invalidate_student_all_sessions(redis, student_id)
            # 失效可用学员列表缓存（需要遍历所有学期）
            cache_pattern = f"{BadmintonCacheKeys.AVAILABLE_STUDENTS}:*:*:*"
            await BadmintonCache.delete_pattern(redis, cache_pattern)
        except Exception as e:
            logger.error(f"失效学员相关缓存失败: student_id={student_id}, error={e}")
            success = False
        return success

    @staticmethod
    async def invalidate_all_class_related(redis: Redis, class_id: int) -> bool:
        """失效班级相关的所有缓存"""
        success = True
        try:
            # 失效班级详情
            await BadmintonCacheInvalidator.invalidate_class_detail(redis, class_id)
            # 失效班级时间段缓存（所有星期）
            for day_of_week in range(7):
                await BadmintonCacheInvalidator.invalidate_class_time_slots(redis, class_id, day_of_week)
            # 失效可用学员列表缓存
            cache_pattern = f"{BadmintonCacheKeys.AVAILABLE_STUDENTS}:*:*:*"
            await BadmintonCache.delete_pattern(redis, cache_pattern)
        except Exception as e:
            logger.error(f"失效班级相关缓存失败: class_id={class_id}, error={e}")
            success = False
        return success


# ============================================================================
# 缓存预热工具类
# ============================================================================

class BadmintonCacheWarmer:
    """羽毛球业务缓存预热工具类"""

    @staticmethod
    async def warmup_time_slot_dict(redis: Redis) -> dict:
        """预热时间段字典"""
        from app.api.v1.module_system.dict.service import DictDataService
        try:
            # 触发加载，会自动缓存
            time_slot_data = await get_time_slot_dict_with_cache(redis, 'badminton_time_slot')
            logger.info(f"✅ 缓存预热成功: 时间段字典")
            return {"status": "success", "data": time_slot_data}
        except Exception as e:
            logger.error(f"❌ 缓存预热失败: 时间段字典, error={e}")
            return {"status": "error", "message": str(e)}

    @staticmethod
    async def warmup_active_semesters(redis: Redis, db: AsyncSession = None) -> dict:
        """预热活跃学期列表"""
        try:
            from app.plugin.module_badminton.semester.crud import SemesterCRUD
            from app.plugin.module_badminton.class_.crud import ClassCRUD
            from app.api.v1.module_system.auth.schema import AuthSchema
            from sqlalchemy import select, or_
            from app.plugin.module_badminton.semester.model import SemesterModel

            # 查询活跃学期
            auth = AuthSchema(db=db, check_data_scope=False) if db else AuthSchema(db=None, check_data_scope=False)

            if not db:
                raise ValueError("warmup_active_semesters 需要数据库会话参数 db")

            # 尝试多种状态：active, planning（只要是未归档的学期）
            stmt = (
                select(SemesterModel)
                .where(
                    or_(
                        SemesterModel.status == "active",
                        SemesterModel.status == "planning"
                    )
                )
                .order_by(SemesterModel.start_date.desc())
            )
            result = await db.execute(stmt)
            semesters = result.scalars().all()

            logger.info(f"缓存预热: 找到 {len(semesters)} 个活跃/进行中/规划中的学期")

            # 预热每个学期的班级列表
            for semester in semesters:
                cache_key = f"{BadmintonCacheKeys.SEMESTER_CLASSES}:{semester.id}"
                classes = await ClassCRUD(auth).list_crud(
                    search={"semester_id": ("eq", semester.id)}
                )

                # 缓存班级列表
                class_list = [{"id": c.id, "name": c.name, "class_type": c.class_type.value if c.class_type else None} for c in classes]
                await BadmintonCache.set_json(redis, cache_key, class_list, CacheExpireTime.SEMESTER_CLASSES)
                logger.info(f"  ✅ 缓存学期 {semester.name} (状态: {semester.status}) 的班级列表: {len(classes)} 个班级")

            return {"status": "success", "count": len(semesters)}
        except Exception as e:
            logger.error(f"❌ 缓存预热失败: 活跃学期列表, error={e}")
            return {"status": "error", "message": str(e)}

    @staticmethod
    async def warmup_coaches(redis: Redis, db: AsyncSession = None) -> dict:
        """
        预热教练列表

        Args:
            redis: Redis 客户端
            db: 数据库会话（可选）

        Returns:
            dict: 预热结果
        """
        from sqlalchemy import select

        try:
            if not db:
                raise ValueError("warmup_coaches 需要数据库会话参数 db")

            from app.api.v1.module_system.user.model import UserModel, UserRolesModel
            from app.api.v1.module_system.role.model import RoleModel

            # 查询所有教练角色用户
            stmt = (
                select(UserModel)
                .join(UserRolesModel, UserModel.id == UserRolesModel.user_id)
                .join(RoleModel, UserRolesModel.role_id == RoleModel.id)
                .where((RoleModel.name == "教练") | (RoleModel.code == "教练"))
                .where(UserModel.status == "0")  # 启用状态
                .order_by(UserModel.id)
            )
            result = await db.execute(stmt)
            coaches = result.scalars().all()

            coaches_data = [
                {
                    "id": c.id,
                    "username": c.username,
                    "nickname": c.name,
                    "mobile": c.mobile,
                }
                for c in coaches
            ]

            cache_key = "badminton:coaches"
            await BadmintonCache.set_json(redis, cache_key, coaches_data, CacheExpireTime.CLASS_DETAIL)

            return {
                "status": "success",
                "count": len(coaches_data),
                "message": f"成功预热 {len(coaches_data)} 个教练信息",
            }
        except Exception as e:
            logger.error(f"❌ 缓存预热失败: 教练列表, error={e}")
            return {"status": "error", "message": str(e)}

    @staticmethod
    async def warmup_all(redis: Redis, db: AsyncSession = None) -> dict:
        """预热所有常用缓存

        Args:
            redis: Redis 客户端
            db: 数据库会话（可选，用于需要数据库查询的预热）

        Returns:
            dict: 所有预热结果
        """
        logger.info("🚀 开始羽毛球业务缓存预热...")
        
        results = {}
        
        # 预热时间段字典（不需要数据库）
        results["time_slot"] = await BadmintonCacheWarmer.warmup_time_slot_dict(redis)

        # 预热活跃学期和班级列表（需要数据库）
        if db:
            results["semesters"] = await BadmintonCacheWarmer.warmup_active_semesters(redis, db)
        else:
            results["semesters"] = {"status": "skipped", "message": "未提供数据库会话"}

        # 预热教练列表（需要数据库）
        if db:
            results["coaches"] = await BadmintonCacheWarmer.warmup_coaches(redis, db)
        else:
            results["coaches"] = {"status": "skipped", "message": "未提供数据库会话"}
        
        success_count = sum(1 for r in results.values() if r.get("status") == "success")
        
        logger.info(f"✅ 羽毛球业务缓存预热完成: {success_count}/{len(results)} 成功")
        
        return results