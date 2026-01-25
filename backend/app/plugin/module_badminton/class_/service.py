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

        result = await ClassCRUD(auth).page_crud(
            offset=offset,
            limit=page_size,
            order_by=order_by_list,
            search=search_dict,
            preload=["semester", "coach_user"],
            out_schema=ClassOutSchema
        )
        
        return PaginatedResponse(
            total=result["total"],
            page_no=page_no,
            page_size=page_size,
            items=result["items"]
        ).model_dump()

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
    async def get_available_time_slots(cls, auth: AuthSchema, class_id: int) -> dict:
        """
        获取班级可用时间段

        根据班级类型返回不同的时间段：
        - 固定班（FIXED）：返回该班级每周固定的上课时间段，这些时间段会重复total_sessions次
        - 自选天（FLEXIBLE）：返回该班级所有可选时间段，学员需要从中选择每周课次数量（不是总课时数）

        Args:
            auth: 认证信息
            class_id: 班级ID

        Returns:
            dict: 包含班级信息、类型和可用时间段的字典
        """
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
                
                # 遍历每一天的时间段配置
                slot_id = 1
                for day, slots in time_slots_config.items():
                    if slots:  # 如果该天有可选时间段
                        day_index = day_names.index(day) if day in day_names else 0
                        for slot_code in slots:
                            if slot_code in time_slot_names:
                                time_range = time_slot_names[slot_code]
                                start_time, end_time = time_range.split('-')
                                
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
                                slot_id += 1
                                
            except json.JSONDecodeError:
                # 如果JSON解析失败，返回空列表
                pass

        # 计算每周课次（总课时数 / 周数）
        # 假设学期为16周（可以根据实际情况调整）
        weeks_per_semester = 16
        sessions_per_week = class_obj.total_sessions // weeks_per_semester if weeks_per_semester > 0 else 0

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

        return result
