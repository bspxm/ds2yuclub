"""
leave模块 - Service服务层
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
from ..response import SimpleResponse

from app.api.v1.module_system.auth.schema import AuthSchema

# ============================================================================
# 请假管理服务
# ============================================================================

class LeaveRequestService:
    """请假管理服务层"""

    @classmethod
    async def submit_service(cls, auth: AuthSchema, leave_data: dict) -> dict:
        """提交请假申请"""
        student = await StudentCRUD(auth).get_by_id_crud(leave_data["student_id"])
        if not student:
            raise CustomException(msg="学员不存在")

        leave = await LeaveRequestCRUD(auth).submit_crud(leave_data)
        return SimpleResponse(
            success=True,
            message="请假申请已提交",
            data={"leave_id": leave.id}
        ).model_dump()

    @classmethod
    async def approve_service(cls, auth: AuthSchema, leave_id: int, notes: Optional[str] = None) -> dict:
        """批准请假申请"""
        leave = await LeaveRequestCRUD(auth).approve_crud(
            leave_id=leave_id,
            reviewed_by=auth.user.id,
            notes=notes
        )
        if not leave:
            raise CustomException(msg="请假申请不存在")
        return SimpleResponse(
            success=True,
            message="请假申请已批准"
        ).model_dump()

    @classmethod
    async def get_pending_service(cls, auth: AuthSchema) -> list[dict]:
        """获取待审核的请假申请"""
        requests = await LeaveRequestCRUD(auth).get_pending_requests_crud()

        result = []
        for req in requests:
            result.append({
                "id": req.id,
                "student": StudentOutSchema.model_validate(req.student).model_dump(),
                "leave_date": req.leave_date,
                "reason": req.leave_reason,
                "status": req.leave_status,
                "created_by": req.created_by.username if req.created_by else None,
                "created_time": req.created_time
            })

        return result
