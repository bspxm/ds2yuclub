"""
attendance模块 - Service服务层
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
from ..team.schema import (
    ClassAttendanceCreateSchema,
    ClassAttendanceUpdateSchema,
    ClassAttendanceOutSchema,
    ClassAttendanceQueryParam,
)
from app.common.response import PaginatedResponse
from ..response import SimpleResponse

from app.api.v1.module_system.auth.schema import AuthSchema

# ============================================================================
# 考勤记录管理服务
# ============================================================================


class ClassAttendanceService:
    """考勤记录管理服务层"""

    @classmethod
    async def detail_service(cls, auth: AuthSchema, attendance_id: int) -> dict:
        """获取考勤记录详情"""
        attendance = await ClassAttendanceCRUD(auth).get_by_id_crud(
            id=attendance_id,
            preload=[
                "student",
                "class_ref",
                "schedule",
                "purchase",
                "coach_user",
                "created_by",
                "updated_by",
            ],
        )
        if not attendance:
            raise CustomException(msg="考勤记录不存在")
        return ClassAttendanceOutSchema.model_validate(attendance).model_dump()

    @classmethod
    async def list_service(
        cls,
        auth: AuthSchema,
        search: Optional[dict] = None,
        order_by: Optional[list[dict]] = None,
    ) -> list[dict]:
        """考勤记录列表查询"""
        attendances = await ClassAttendanceCRUD(auth).list_crud(
            search=search,
            order_by=order_by,
            preload=["student", "class_ref", "schedule", "purchase", "coach_user"],
        )
        return [
            ClassAttendanceOutSchema.model_validate(attendance).model_dump()
            for attendance in attendances
        ]

    @classmethod
    async def page_service(
        cls,
        auth: AuthSchema,
        page_no: int,
        page_size: int,
        search: Optional[dict | ClassAttendanceQueryParam] = None,
        order_by: Optional[list[dict]] = None,
    ) -> dict:
        """考勤记录分页查询"""
        # 将QueryParam对象转换为字典
        if isinstance(search, ClassAttendanceQueryParam):
            search_dict = vars(search)
        else:
            search_dict = search or {}

        order_by_list = order_by or [{"id": "asc"}]
        offset = (page_no - 1) * page_size

        # 不使用 out_schema，直接获取原始对象以避免加载过多关联数据
        result = await ClassAttendanceCRUD(auth).page_crud(
            offset=offset,
            limit=page_size,
            order_by=order_by_list,
            search=search_dict,
            preload=["student", "class_ref", "schedule", "purchase", "coach_user"],
            out_schema=None,
        )

        # 手动构建返回数据，只包含必要的字段
        items = []
        for attendance in result["items"]:
            item = {
                "id": attendance.id,
                "uuid": attendance.uuid,
                "student_id": attendance.student_id,
                "class_id": attendance.class_id,
                "schedule_id": attendance.schedule_id,
                "purchase_id": attendance.purchase_id,
                "attendance_date": attendance.attendance_date.isoformat()
                if attendance.attendance_date
                else None,
                "start_time": attendance.start_time.isoformat()
                if attendance.start_time
                else None,
                "end_time": attendance.end_time.isoformat()
                if attendance.end_time
                else None,
                "duration_minutes": attendance.duration_minutes,
                "attendance_status": attendance.attendance_status.value
                if attendance.attendance_status
                else None,
                "is_leave": attendance.is_leave,
                "session_deducted": attendance.session_deducted,
                "is_auto_deduct": attendance.is_auto_deduct,
                "notes": attendance.description,
                "status": attendance.status,
                "created_time": attendance.created_time.isoformat()
                if attendance.created_time
                else None,
                "updated_time": attendance.updated_time.isoformat()
                if attendance.updated_time
                else None,
                # 关联对象
                "student": {
                    "id": attendance.student.id,
                    "name": attendance.student.name,
                }
                if attendance.student
                else None,
                "class_ref": {
                    "id": attendance.class_ref.id,
                    "name": attendance.class_ref.name,
                }
                if attendance.class_ref
                else None,
                "schedule": {
                    "id": attendance.schedule.id,
                    "schedule_date": attendance.schedule.schedule_date.isoformat()
                    if attendance.schedule and attendance.schedule.schedule_date
                    else None,
                }
                if attendance.schedule
                else None,
                "purchase": {
                    "id": attendance.purchase.id,
                    "purchase_date": attendance.purchase.purchase_date.isoformat()
                    if attendance.purchase and attendance.purchase.purchase_date
                    else None,
                }
                if attendance.purchase
                else None,
                "coach_user": {
                    "id": attendance.coach_user.id,
                    "name": attendance.coach_user.name,
                }
                if attendance.coach_user
                else None,
            }
            items.append(item)

        return {
            "total": result["total"],
            "page_no": page_no,
            "page_size": page_size,
            "items": items,
        }

    @classmethod
    async def create_service(
        cls, auth: AuthSchema, data: ClassAttendanceCreateSchema
    ) -> dict:
        """创建考勤记录"""
        from datetime import timedelta
        from ..enums import AttendanceStatusEnum

        # 检查考勤记录是否重复（同一学员、同一班级、同一时间）
        # TODO: 实现重复考勤检查

        # 如果是请假记录，设置不扣课时
        if data.attendance_status == AttendanceStatusEnum.LEAVE:
            # 请假不扣课时
            data_dict = data.model_dump()
            data_dict["session_deducted"] = 0
            data_dict["is_auto_deduct"] = False

            # 创建请假考勤记录
            attendance = await ClassAttendanceCRUD(auth).create_crud(
                data=ClassAttendanceCreateSchema(**data_dict)
            )
            if not attendance:
                raise CustomException(msg="创建请假考勤记录失败")

            # 自动创建补课记录（下周同一时间）
            try:
                # 计算下周同一时间（增加7天）
                from datetime import datetime

                # 解析日期和时间
                attendance_date = datetime.strptime(
                    str(data.attendance_date), "%Y-%m-%d"
                ).date()
                makeup_date = attendance_date + timedelta(days=7)

                # 创建补课记录数据
                makeup_data = data.model_dump()
                makeup_data["attendance_status"] = AttendanceStatusEnum.MAKEUP
                makeup_data["is_makeup"] = True
                makeup_data["makeup_date"] = makeup_date.isoformat()
                makeup_data["attendance_date"] = makeup_date.isoformat()
                makeup_data["original_attendance_id"] = attendance.id
                makeup_data["makeup_notes"] = (
                    f"请假自动顺延补课，原请假日期：{attendance_date}"
                )

                # 创建补课记录
                makeup_attendance = await ClassAttendanceCRUD(auth).create_crud(
                    data=ClassAttendanceCreateSchema(**makeup_data)
                )

                # 更新原请假记录的关联
                from ..attendance.model import ClassAttendanceModel
                from app.core.database import async_session

                async with async_session() as session:
                    db_attendance = await session.get(
                        ClassAttendanceModel, attendance.id
                    )
                    if db_attendance:
                        db_attendance.makeup_attendance = makeup_attendance
                        await session.commit()

                return SimpleResponse(
                    success=True,
                    message="请假考勤记录创建成功，已自动安排下周补课",
                    data={
                        "leave_attendance": ClassAttendanceOutSchema.model_validate(
                            attendance
                        ).model_dump(),
                        "makeup_attendance": ClassAttendanceOutSchema.model_validate(
                            makeup_attendance
                        ).model_dump(),
                    },
                ).model_dump()

            except Exception as e:
                # 如果创建补课记录失败，只返回请假记录
                return SimpleResponse(
                    success=True,
                    message=f"请假考勤记录创建成功，但补课安排失败：{str(e)}",
                    data=ClassAttendanceOutSchema.model_validate(
                        attendance
                    ).model_dump(),
                ).model_dump()
        else:
            # 非请假记录，正常创建
            attendance = await ClassAttendanceCRUD(auth).create_crud(data=data)
            if not attendance:
                raise CustomException(msg="创建考勤记录失败")
            return SimpleResponse(
                success=True,
                message="考勤记录创建成功",
                data=ClassAttendanceOutSchema.model_validate(attendance).model_dump(),
            ).model_dump()

    @classmethod
    async def update_service(
        cls, auth: AuthSchema, attendance_id: int, data: ClassAttendanceUpdateSchema
    ) -> dict:
        """更新考勤记录"""
        attendance = await ClassAttendanceCRUD(auth).update_crud(
            id=attendance_id, data=data
        )
        if not attendance:
            raise CustomException(msg="考勤记录不存在或更新失败")
        return SimpleResponse(
            success=True,
            message="考勤记录更新成功",
            data=ClassAttendanceOutSchema.model_validate(attendance).model_dump(),
        ).model_dump()

    @classmethod
    async def delete_service(cls, auth: AuthSchema, attendance_ids: list[int]) -> dict:
        """删除考勤记录"""
        await ClassAttendanceCRUD(auth).delete_crud(ids=attendance_ids)
        return SimpleResponse(success=True, message="考勤记录删除成功").model_dump()

    @classmethod
    async def get_by_student_service(
        cls, auth: AuthSchema, student_id: int
    ) -> list[dict]:
        """获取指定学员的所有考勤记录"""
        search = {"student_id": ("eq", student_id)}
        attendances = await ClassAttendanceCRUD(auth).list_crud(
            search=search,
            preload=["student", "class_ref", "schedule", "purchase", "coach_user"],
        )
        return [
            ClassAttendanceOutSchema.model_validate(attendance).model_dump()
            for attendance in attendances
        ]

    @classmethod
    async def get_by_class_service(cls, auth: AuthSchema, class_id: int) -> list[dict]:
        """获取指定班级的所有考勤记录"""
        search = {"class_id": ("eq", class_id)}
        attendances = await ClassAttendanceCRUD(auth).list_crud(
            search=search,
            preload=["student", "class_ref", "schedule", "purchase", "coach_user"],
        )
        return [
            ClassAttendanceOutSchema.model_validate(attendance).model_dump()
            for attendance in attendances
        ]
