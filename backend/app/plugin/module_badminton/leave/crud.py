"""
leave模块 - CRUD数据操作层
"""

from typing import Optional, List, Dict, Any, Sequence

from sqlalchemy.orm import selectinload

from app.api.v1.module_system.auth.schema import AuthSchema
from app.core.base_crud import CRUDBase
from app.core.database import SessionDep

from .model import *

# ============================================================================
# 请假申请 CRUD
# ============================================================================

class LeaveRequestCRUD(CRUDBase[LeaveRequestModel, dict, dict]):
    """请假申请数据层"""

    def __init__(self, auth: AuthSchema) -> None:
        super().__init__(model=LeaveRequestModel, auth=auth)

    async def submit_crud(self, leave_data: dict) -> Optional[LeaveRequestModel]:
        """提交请假申请"""
        return await self.create(data=leave_data)

    async def approve_crud(self, leave_id: int, reviewed_by: int, notes: Optional[str] = None) -> Optional[LeaveRequestModel]:
        """批准请假申请"""
        return await self.update(leave_id, {
            "status": "approved",
            "reviewed_by": reviewed_by,
            "reviewed_time": datetime.now(),
            "review_notes": notes
        })

    async def get_pending_requests_crud(self) -> Sequence[LeaveRequestModel]:
        """获取待审核的请假申请"""
        return await self.list(
            search={"status": ("eq", "pending")},
            order_by=[{"leave_date": "asc"}],
            preload=[
                selectinload(LeaveRequestModel.student).noload("*"),
                selectinload(LeaveRequestModel.processed_by).noload("*"),
            ]
        )

    async def page_crud(self, offset: int, limit: int, order_by: list[dict[str, str]], search: dict, out_schema: type, preload: list[str] | None = None) -> dict:
        """请假申请分页查询"""
        return await self.page(offset=offset, limit=limit, order_by=order_by, search=search, out_schema=out_schema, preload=preload)
