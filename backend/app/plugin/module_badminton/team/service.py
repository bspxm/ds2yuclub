"""
class_模块 - Service服务层
"""

import json
import time as time_module
from datetime import date, datetime, timedelta
from typing import Optional, List, Dict, Any
from redis.asyncio.client import Redis

from sqlalchemy.orm import Session, selectinload, noload

from app.api.v1.module_system.user.service import UserService
from app.core.base_crud import BaseCRUD
from app.core.database import SessionDep
from app.core.exceptions import CustomException
from app.core.logger import logger

from .model import *
from .crud import *
from .schema import *
from app.common.response import PaginatedResponse
from ..response import SimpleResponse

from app.api.v1.module_system.auth.schema import AuthSchema
from ..cache_utils import BadmintonCache, BadmintonCacheKeys, CacheExpireTime


def _class_preload_options() -> list:
    """构建班级的预加载选项，使用 noload("*") 阻止级联加载"""
    return [
        selectinload(ClassModel.semester).noload("*"),
        selectinload(ClassModel.coach_user).noload("*"),
    ]


# ============================================================================
# 班级管理服务
# ============================================================================

class ClassService:
    """班级管理服务层"""

    @classmethod
    async def detail_service(cls, auth: AuthSchema, class_id: int) -> dict:
        """获取班级详情（使用视图优化性能）"""
        import asyncio
        # 使用视图查询班级信息（已包含学期和教练信息）
        class_obj = await ClassListCRUD(auth).get_by_id_crud(id=class_id)
        if not class_obj:
            raise CustomException(msg="班级不存在")
        
        # 并行查询创建人和更新人
        from app.api.v1.module_system.user.crud import UserCRUD
        related_queries = []
        
        if class_obj.created_id:
            related_queries.append(("creator", UserCRUD(auth).get_by_id_crud(id=class_obj.created_id)))
        
        if class_obj.updated_id:
            related_queries.append(("updater", UserCRUD(auth).get_by_id_crud(id=class_obj.updated_id)))
        
        # 等待查询完成
        related_results = await asyncio.gather(*[r[1] for r in related_queries], return_exceptions=True)
        
        # 提取结果
        created_by = None
        updated_by = None
        for i, (query_name, result) in enumerate(zip([r[0] for r in related_queries], related_results)):
            if isinstance(result, Exception):
                logger.error(f"查询{query_name}信息失败: {result}")
            else:
                if query_name == "creator":
                    created_by = result
                elif query_name == "updater":
                    updated_by = result
        
        # 构建返回数据
        item = {
            'id': class_obj.id,
            'uuid': class_obj.uuid,
            'semester_id': class_obj.semester_id,
            'name': class_obj.name,
            'class_type': class_obj.class_type,
            'coach_id': class_obj.coach_id,
            'total_sessions': class_obj.total_sessions,
            'sessions_per_week': class_obj.sessions_per_week,
            'session_duration': class_obj.session_duration,
            'session_price': class_obj.session_price,
            'max_students': class_obj.max_students,
            'min_students': class_obj.min_students,
            'current_students': class_obj.current_students,
            'start_date': class_obj.start_date.isoformat() if class_obj.start_date else None,
            'end_date': class_obj.end_date.isoformat() if class_obj.end_date else None,
            'weekly_schedule': class_obj.weekly_schedule,
            'time_slots_json': class_obj.time_slots_json,
            'location': class_obj.location,
            'class_status': class_obj.class_status,
            'is_active': class_obj.is_active,
            'enrollment_open': class_obj.enrollment_open,
            'fee_per_session': class_obj.fee_per_session,
            'description': class_obj.description,
            'notes': class_obj.notes,
            'created_time': class_obj.created_time.isoformat() if class_obj.created_time else None,
            'updated_time': class_obj.updated_time.isoformat() if class_obj.updated_time else None,
            # 视图字段 - 学期信息
            'semester': {
                'id': class_obj.semester_ref_id,
                'name': class_obj.semester_name
            } if class_obj.semester_ref_id else None,
            # 视图字段 - 教练信息
            'coach_user': {
                'id': class_obj.coach_user_id,
                'name': class_obj.coach_user_name
            } if class_obj.coach_user_id else None,
            # 创建人和更新人
            'created_by': {'id': created_by.id, 'name': created_by.name} if created_by else None,
            'updated_by': {'id': updated_by.id, 'name': updated_by.name} if updated_by else None,
        }
        
        return item

    @classmethod
    async def list_service(cls, auth: AuthSchema, search: Optional[dict] = None, order_by: Optional[list[dict]] = None) -> list[dict]:
        """班级列表查询"""
        classes = await ClassCRUD(auth).list_crud(
            search=search,
            order_by=order_by,
            preload=_class_preload_options()
        )
        return [ClassOutSchema.model_validate(class_obj).model_dump() for class_obj in classes]

    @classmethod
    async def page_service(cls, auth: AuthSchema, page_no: int, page_size: int, search: Optional[dict | ClassQueryParam] = None, order_by: Optional[list[dict]] = None) -> dict:
        """班级分页查询（使用视图优化性能）"""
        # 将QueryParam对象转换为字典
        if isinstance(search, ClassQueryParam):
            search_dict = vars(search)
        else:
            search_dict = search or {}

        order_by_list = order_by or [{'id': 'asc'}]
        offset = (page_no - 1) * page_size

        # 使用视图模型查询，避免预加载性能问题
        # 视图已经包含了学期和教练信息，不需要预加载
        result = await ClassListCRUD(auth).page_crud(
            offset=offset,
            limit=page_size,
            order_by=order_by_list,
            search=search_dict,
            preload=[],  # 视图不需要预加载
            out_schema=None
        )

        # 手动构建返回数据，使用视图的字段
        items = []
        for class_obj in result["items"]:
            item = {
                'id': class_obj.id,
                'uuid': class_obj.uuid,
                'semester_id': class_obj.semester_id,
                'name': class_obj.name,
                'class_type': class_obj.class_type,
                'coach_id': class_obj.coach_id,
                'total_sessions': class_obj.total_sessions,
                'session_duration': class_obj.session_duration,
                'session_price': class_obj.session_price,
                'max_students': class_obj.max_students,
                'min_students': class_obj.min_students,
                'current_students': class_obj.current_students,
                'start_date': class_obj.start_date.isoformat() if class_obj.start_date else None,
                'end_date': class_obj.end_date.isoformat() if class_obj.end_date else None,
                'weekly_schedule': class_obj.weekly_schedule,
                'time_slots_json': class_obj.time_slots_json,
                'location': class_obj.location,
                'class_status': class_obj.class_status,
                'is_active': class_obj.is_active,
                'enrollment_open': class_obj.enrollment_open,
                'fee_per_session': class_obj.fee_per_session,
                'description': class_obj.description,
                'notes': class_obj.notes,
                'created_time': class_obj.created_time.isoformat() if class_obj.created_time else None,
                'updated_time': class_obj.updated_time.isoformat() if class_obj.updated_time else None,
                # 视图字段 - 学期信息
                'semester': {
                    'id': class_obj.semester_ref_id,
                    'name': class_obj.semester_name
                } if class_obj.semester_ref_id else None,
                # 视图字段 - 教练信息
                'coach_user': {
                    'id': class_obj.coach_user_id,
                    'name': class_obj.coach_user_name
                } if class_obj.coach_user_id else None,
            }
            items.append(item)

        return {
            "total": result["total"],
            "page_no": page_no,
            "page_size": page_size,
            "items": items
        }

    @classmethod
    async def create_service(cls, auth: AuthSchema, data: ClassCreateSchema) -> dict:
        """创建班级"""
        # 检查班级名称是否重复
        # TODO: 实现名称重复检查
        
        class_obj = await ClassCRUD(auth).create_crud(data=data)
        if not class_obj:
            raise CustomException(msg="创建班级失败")
        return SimpleResponse(
            success=True,
            message="班级创建成功",
            data=ClassOutSchema.model_validate(class_obj).model_dump()
        ).model_dump()

    @classmethod
    async def update_service(cls, auth: AuthSchema, class_id: int, data: ClassUpdateSchema) -> dict:
        """更新班级"""
        class_obj = await ClassCRUD(auth).update_crud(id=class_id, data=data)
        if not class_obj:
            raise CustomException(msg="班级不存在或更新失败")
        return SimpleResponse(
            success=True,
            message="班级更新成功",
            data=ClassOutSchema.model_validate(class_obj).model_dump()
        ).model_dump()

    @classmethod
    async def delete_service(cls, auth: AuthSchema, class_ids: list[int]) -> dict:
        """删除班级"""
        await ClassCRUD(auth).delete_crud(ids=class_ids)
        return SimpleResponse(
            success=True,
            message="班级删除成功"
        ).model_dump()

    @classmethod
    async def get_by_semester_service(cls, auth: AuthSchema, semester_id: int) -> list[dict]:
        """获取指定学期的所有班级"""
        search = {"semester_id": ("eq", semester_id)}
        classes = await ClassCRUD(auth).list_crud(
            search=search,
            order_by=[{'id': 'asc'}],
            preload=_class_preload_options()
        )
        return [ClassOutSchema.model_validate(class_obj).model_dump() for class_obj in classes]

    @classmethod
    async def get_available_time_slots(cls, auth: AuthSchema, redis: Redis, class_id: int, day_of_week: int | None = None) -> dict:
        """
        获取班级可用时间段（带Redis缓存）

        根据班级类型返回不同的时间段：
        - 固定班（FIXED）：返回该班级每周固定的上课时间段，这些时间段会重复total_sessions次
        - 自选天（FLEXIBLE）：返回该班级所有可选时间段，学员需要从中选择每周课次数量（不是总课时数）

        如果指定了 day_of_week（星期几，0=周日，1=周一，...，6=周六），则只返回该星期的可用时间段

        Args:
            auth: 认证信息
            redis: Redis客户端
            class_id: 班级ID
            day_of_week: 星期几（可选，0=周日，1=周一，...，6=周六）

        Returns:
            dict: 包含班级信息、类型和可用时间段的字典
        """
        logger.info(f"Service接收参数: class_id={class_id}, day_of_week={day_of_week}, redis_type={type(redis).__name__}")

        # 性能监控开始
        total_start = time_module.time()

        # 初始化所有计时变量
        cache_start = cache_end = db_start = db_end = json_start = json_end = cache_write_start = cache_write_end = 0

        # 尝试从Redis缓存获取（缓存整个班级的所有时间段，避免多次查询）
        cache_key = f"{BadmintonCacheKeys.CLASS_TIME_SLOTS}:{class_id}"

        cache_start = time_module.time()
        try:
            cached_result = await BadmintonCache.get_json(redis, cache_key)
            cache_end = time_module.time()
            logger.info(f"Redis缓存查询耗时: {cache_end - cache_start:.3f}秒")

            if cached_result is not None:
                logger.info(f"从缓存获取班级可用时间段: class_id={class_id}, result_type={type(cached_result)}, time_slots数量: {len(cached_result.get('time_slots', []))}")
                # 确保返回的是字典类型且时间段不为空
                if isinstance(cached_result, dict) and "time_slots" in cached_result and len(cached_result["time_slots"]) > 0:
                    # 不在后端过滤 day_of_week，返回完整的时间段列表
                    # 前端会根据选择的日期进行过滤
                    logger.info(f"从缓存返回完整时间段列表（包含所有星期几），时间段数: {len(cached_result['time_slots'])}")
                    return cached_result
                else:
                    logger.warning(f"缓存数据无效（时间段为空或类型不正确），将重新查询")
        except Exception as e:
            cache_end = time_module.time()
            logger.error(f"获取缓存异常: class_id={class_id}, error={e}, 耗时: {cache_end - cache_start:.3f}秒")

        # 获取班级信息（优化：只加载必要的字段，不加载关联数据）
        db_start = time_module.time()
        class_obj = await ClassCRUD(auth).get_by_id_crud(
            id=class_id,
            preload=None  # 不加载关联数据，减少查询时间
        )
        db_end = time_module.time()
        logger.info(f"数据库查询耗时: {db_end - db_start:.3f}秒")

        if not class_obj:
            raise CustomException(msg="班级不存在")

        # 解析时间段JSON配置
        json_start = time_module.time()
        time_slots = []

        if class_obj.time_slots_json:
            try:
                time_slots_config = json.loads(class_obj.time_slots_json)
                json_end = time_module.time()
                logger.info(f"JSON解析耗时: {json_end - json_start:.3f}秒")
                logger.info(f"解析time_slots_json: {time_slots_config}")
            except json.JSONDecodeError:
                json_end = time_module.time()
                logger.warning(f"JSON解析失败: 耗时 {json_end - json_start:.3f}秒")
                time_slots_config = {}

        # 定义星期映射
        day_names = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

        # 定义时间段映射
        time_slot_names = {
            'A': '08:00-09:30',
            'B': '09:30-11:00',
            'C': '14:00-15:30',
            'D': '15:30-17:00',
            'E': '18:00-19:30'
        }

        logger.info(f"筛选时间段 - day_of_week={day_of_week}, time_slots_config={time_slots_config}")

        # 遍历每一天的时间段配置（不按 day_of_week 过滤，生成所有星期几的时间段）
        for day, slots in time_slots_config.items():

            if slots:  # 如果该天有可选时间段
                for slot_code in slots:
                    if slot_code in time_slot_names:
                        time_range = time_slot_names[slot_code]
                        start_time, end_time = time_range.split('-')
                        day_index = day_names.index(day) if day in day_names else 0
                        # 生成唯一ID：使用 day_index + slot_code 的方式
                        # 例如：周六A = "6A", 周日A = "0A"
                        slot_id = f"{day_index}{slot_code}"

                        time_slots.append({
                            "id": slot_id,
                            "day_of_week": day,
                            "day": day,
                            "day_index": day_index,
                            "slot_code": slot_code,
                            "start_time": start_time,
                            "end_time": end_time,
                            "duration_minutes": 90,
                            "location": class_obj.location,
                            "display_text": f"{day} {time_range}"
                        })

        # 使用数据库字段中的每周课次
        sessions_per_week = class_obj.sessions_per_week or 0

        # 返回结果
        result = {
            "class_id": class_obj.id,
            "class_name": class_obj.name,
            "class_type": class_obj.class_type.value if class_obj.class_type else None,
            "total_sessions": class_obj.total_sessions,
            "sessions_per_week": sessions_per_week,
            "time_slots": time_slots,
            "class_type_display": "固定天训练" if class_obj.class_type and class_obj.class_type.value == "fixed" else "自选天训练"
        }

        logger.info(f"获取班级可用时间段成功：班级ID={class_id}, 星期几={day_of_week}, 时间段数={len(time_slots)}")

        # 存入Redis缓存（缓存所有时间段，不区分星期几）
        cache_write_start = time_module.time()
        await BadmintonCache.set_json(redis, cache_key, result, CacheExpireTime.CLASS_TIME_SLOTS)
        cache_write_end = time_module.time()
        logger.info(f"Redis缓存写入耗时: {cache_write_end - cache_write_start:.3f}秒")
        logger.info(f"班级可用时间段已缓存: class_id={class_id}, 缓存键={cache_key}")

        # 性能监控结束
        total_end = time_module.time()
        logger.info(f"总耗时: {total_end - total_start:.3f}秒 (缓存查询: {cache_end - cache_start:.3f}s | 数据库查询: {db_end - db_start:.3f}s | JSON解析: {json_end - json_start:.3f}s | 缓存写入: {cache_write_end - cache_write_start:.3f}s)")

        return result
