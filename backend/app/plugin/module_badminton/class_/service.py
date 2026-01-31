"""
class_模块 - Service服务层
"""

from datetime import date, datetime, timedelta
from typing import Optional, List, Dict, Any

from sqlalchemy.orm import Session

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

# ============================================================================
# 班级管理服务
# ============================================================================

class ClassService:
    """班级管理服务层"""

    @classmethod
    async def detail_service(cls, auth: AuthSchema, class_id: int) -> dict:
        """获取班级详情"""
        class_obj = await ClassCRUD(auth).get_by_id_crud(
            id=class_id,
            preload=["semester", "coach_user", "created_by", "updated_by"]
        )
        if not class_obj:
            raise CustomException(msg="班级不存在")
        return ClassOutSchema.model_validate(class_obj).model_dump()

    @classmethod
    async def list_service(cls, auth: AuthSchema, search: Optional[dict] = None, order_by: Optional[list[dict]] = None) -> list[dict]:
        """班级列表查询"""
        classes = await ClassCRUD(auth).list_crud(
            search=search,
            order_by=order_by,
            preload=["semester", "coach_user"]
        )
        return [ClassOutSchema.model_validate(class_obj).model_dump() for class_obj in classes]

    @classmethod
    async def page_service(cls, auth: AuthSchema, page_no: int, page_size: int, search: Optional[dict | ClassQueryParam] = None, order_by: Optional[list[dict]] = None) -> dict:
        """班级分页查询"""
        # 将QueryParam对象转换为字典
        if isinstance(search, ClassQueryParam):
            search_dict = vars(search)
        else:
            search_dict = search or {}

        order_by_list = order_by or [{'id': 'asc'}]
        offset = (page_no - 1) * page_size

        # 不使用 out_schema，直接获取原始对象以避免加载过多关联数据
        result = await ClassCRUD(auth).page_crud(
            offset=offset,
            limit=page_size,
            order_by=order_by_list,
            search=search_dict,
            preload=["semester", "coach_user"],
            out_schema=None
        )

        # 手动构建返回数据，只包含必要的字段
        items = []
        for class_obj in result["items"]:
            item = {
                'id': class_obj.id,
                'uuid': class_obj.uuid,
                'semester_id': class_obj.semester_id,
                'name': class_obj.name,
                'class_type': class_obj.class_type.value if class_obj.class_type else None,
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
                'class_status': class_obj.class_status.value if class_obj.class_status else None,
                'is_active': class_obj.is_active,
                'enrollment_open': class_obj.enrollment_open,
                'fee_per_session': class_obj.fee_per_session,
                'description': class_obj.description,
                'notes': class_obj.notes,
                'status': class_obj.status,
                'created_time': class_obj.created_time.isoformat() if class_obj.created_time else None,
                'updated_time': class_obj.updated_time.isoformat() if class_obj.updated_time else None,
                # 关联对象
                'semester': {
                    'id': class_obj.semester.id,
                    'name': class_obj.semester.name
                } if class_obj.semester else None,
                'coach_user': {
                    'id': class_obj.coach_user.id,
                    'name': class_obj.coach_user.name
                } if class_obj.coach_user else None,
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
            preload=["semester", "coach_user"]
        )
        return [ClassOutSchema.model_validate(class_obj).model_dump() for class_obj in classes]

    @classmethod
    async def get_available_time_slots(cls, auth: AuthSchema, class_id: int, day_of_week: int | None = None) -> dict:
        """
        获取班级可用时间段

        根据班级类型返回不同的时间段：
        - 固定班（FIXED）：返回该班级每周固定的上课时间段，这些时间段会重复total_sessions次
        - 自选天（FLEXIBLE）：返回该班级所有可选时间段，学员需要从中选择每周课次数量（不是总课时数）
        
        如果指定了 day_of_week（星期几，0=周日，1=周一，...，6=周六），则只返回该星期的可用时间段

        Args:
            auth: 认证信息
            class_id: 班级ID
            day_of_week: 星期几（可选，0=周日，1=周一，...，6=周六）

        Returns:
            dict: 包含班级信息、类型和可用时间段的字典
        """
        logger.info(f"Service接收参数: class_id={class_id}, day_of_week={day_of_week}")
        # 获取班级信息
        class_obj = await ClassCRUD(auth).get_by_id_crud(
            id=class_id,
            preload=["semester", "coach_user"]
        )
        if not class_obj:
            raise CustomException(msg="班级不存在")

        # 解析时间段JSON配置
        import json
        time_slots = []
        
        if class_obj.time_slots_json:
            try:
                time_slots_config = json.loads(class_obj.time_slots_json)
                logger.info(f"解析time_slots_json: {time_slots_config}")
                
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
                
                # 定义时间段ID映射
                time_slot_ids = {
                    'A': 1,
                    'B': 2,
                    'C': 3,
                    'D': 4,
                    'E': 5
                }
                
                logger.info(f"筛选时间段 - day_of_week={day_of_week}, time_slots_config={time_slots_config}")
                
                # 遍历每一天的时间段配置
                for day, slots in time_slots_config.items():
                    # 如果指定了 day_of_week，只处理该星期
                    if day_of_week is not None:
                        day_index = day_names.index(day) if day in day_names else 0
                        logger.info(f"检查星期: day={day}, day_index={day_index}, day_of_week={day_of_week}, 匹配: {day_index == day_of_week}")
                        if day_index != day_of_week:
                            logger.info(f"跳过: day_index({day_index}) != day_of_week({day_of_week})")
                            continue
                        else:
                            logger.info(f"匹配成功: day={day}, day_index={day_index}")
                    
                    if slots:  # 如果该天有可选时间段
                        for slot_code in slots:
                            if slot_code in time_slot_names:
                                time_range = time_slot_names[slot_code]
                                start_time, end_time = time_range.split('-')
                                day_index = day_names.index(day) if day in day_names else 0
                                # 生成唯一ID：使用 day_index * 10 + slot_id 的方式
                                # 例如：周六A = 6*10 + 1 = 61, 周日A = 0*10 + 1 = 1
                                slot_id = day_index * 10 + time_slot_ids[slot_code]
                                
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
                                
            except json.JSONDecodeError:
                # 如果JSON解析失败，返回空列表
                pass

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

        return result
