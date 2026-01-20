"""
schedule模块 - Service服务层
"""

from datetime import date, datetime, timedelta
from typing import Optional, List, Dict, Any

from sqlalchemy.orm import Session

from app.api.v1.module_system.user.service import UserService
from app.core.base_crud import CRUDBase
from app.core.database import SessionDep
from app.core.exceptions import CustomException
from app.core.logger import logger

from .model import *
from .crud import *
from ..class_.schema import (
    ClassScheduleCreateSchema,
    ClassScheduleUpdateSchema,
    ClassScheduleOutSchema,
    ClassScheduleQueryParam
)
from app.common.response import PaginatedResponse

from app.api.v1.module_system.auth.schema import AuthSchema

# ============================================================================
# 排课记录管理服务
# ============================================================================

class ClassScheduleService:
    """排课记录管理服务层"""

    @classmethod
    async def detail_service(cls, auth: AuthSchema, schedule_id: int) -> dict:
        """获取排课记录详情"""
        schedule = await ClassScheduleCRUD(auth).get_by_id_crud(
            id=schedule_id,
            preload=["class_ref", "coach_user", "created_by", "updated_by"]
        )
        if not schedule:
            raise CustomException(msg="排课记录不存在")
        return ClassScheduleOutSchema.model_validate(schedule).model_dump()

    @classmethod
    async def list_service(cls, auth: AuthSchema, search: Optional[dict] = None, order_by: Optional[list[dict]] = None) -> list[dict]:
        """排课记录列表查询"""
        schedules = await ClassScheduleCRUD(auth).list_crud(
            search=search,
            order_by=order_by,
            preload=["class_ref", "coach_user"]
        )
        return [ClassScheduleOutSchema.model_validate(schedule).model_dump() for schedule in schedules]

    @classmethod
    async def page_service(cls, auth: AuthSchema, page_no: int, page_size: int, search: Optional[dict | ClassScheduleQueryParam] = None, order_by: Optional[list[dict]] = None) -> dict:
        """排课记录分页查询"""
        # 将QueryParam对象转换为字典
        if isinstance(search, ClassScheduleQueryParam):
            search_dict = vars(search)
        else:
            search_dict = search or {}
        
        order_by_list = order_by or [{'id': 'asc'}]
        offset = (page_no - 1) * page_size

        result = await ClassScheduleCRUD(auth).page_crud(
            offset=offset,
            limit=page_size,
            order_by=order_by_list,
            search=search_dict,
            preload=["class_ref", "coach_user"],
            out_schema=ClassScheduleOutSchema
        )
        
        return PaginatedResponse(
            total=result["total"],
            page_no=page_no,
            page_size=page_size,
            items=result["items"]
        ).model_dump()

    @classmethod
    async def create_service(cls, auth: AuthSchema, data: ClassScheduleCreateSchema) -> dict:
        """创建排课记录"""
        # 检查排课时间是否冲突（同一班级、同一时间）
        # TODO: 实现时间冲突检查
        
        schedule = await ClassScheduleCRUD(auth).create_crud(data=data)
        if not schedule:
            raise CustomException(msg="创建排课记录失败")
        return SimpleResponse(
            success=True,
            message="排课记录创建成功",
            data=ClassScheduleOutSchema.model_validate(schedule).model_dump()
        ).model_dump()

    @classmethod
    async def update_service(cls, auth: AuthSchema, schedule_id: int, data: ClassScheduleUpdateSchema) -> dict:
        """更新排课记录"""
        schedule = await ClassScheduleCRUD(auth).update_crud(id=schedule_id, data=data)
        if not schedule:
            raise CustomException(msg="排课记录不存在或更新失败")
        return SimpleResponse(
            success=True,
            message="排课记录更新成功",
            data=ClassScheduleOutSchema.model_validate(schedule).model_dump()
        ).model_dump()

    @classmethod
    async def delete_service(cls, auth: AuthSchema, schedule_ids: list[int]) -> dict:
        """删除排课记录"""
        await ClassScheduleCRUD(auth).delete_crud(ids=schedule_ids)
        return SimpleResponse(
            success=True,
            message="排课记录删除成功"
        ).model_dump()

    @classmethod
    async def auto_reschedule_for_leave(cls, auth: AuthSchema, schedule_id: int, student_id: int) -> dict:
        """
        请假自动顺延：当学员请假时，自动预约下周同一时间的补课

        Args:
            auth: 认证信息
            schedule_id: 原排课记录ID
            student_id: 请假学员ID

        Returns:
            dict: 新的排课记录信息
        """
        # 获取原排课记录
        original_schedule = await ClassScheduleCRUD(auth).get_by_id_crud(
            id=schedule_id,
            preload=["class_ref"]
        )
        if not original_schedule:
            raise CustomException(msg="原排课记录不存在")

        # 计算下周同一时间
        if original_schedule.schedule_date and original_schedule.start_time:
            original_date = original_schedule.schedule_date
            next_week_date = original_date + timedelta(days=7)

            # 创建新的排课记录（补课）
            new_schedule_data = ClassScheduleCreateSchema(
                class_id=original_schedule.class_id,
                schedule_date=next_week_date,
                start_time=original_schedule.start_time,
                end_time=original_schedule.end_time,
                schedule_status=ScheduleStatusEnum.SCHEDULED,
                is_makeup=True,  # 标记为补课
                original_schedule_id=schedule_id,  # 关联原排课记录
                notes=f"学员ID:{student_id}请假自动顺延补课"
            )

            new_schedule = await ClassScheduleCRUD(auth).create_crud(data=new_schedule_data)
            if not new_schedule:
                raise CustomException(msg="创建补课排课记录失败")

            logger.info(f"学员{student_id}请假，已自动创建补课排课记录：{new_schedule.id}")

            return SimpleResponse(
                success=True,
                message="请假自动顺延补课已安排",
                data=ClassScheduleOutSchema.model_validate(new_schedule).model_dump()
            ).model_dump()
        else:
            raise CustomException(msg="原排课记录缺少日期或时间信息")
