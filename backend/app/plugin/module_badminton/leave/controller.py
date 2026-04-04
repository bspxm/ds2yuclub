"""
leave模块 - 控制器
请假管理API
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.v1.module_system.auth.schema import AuthSchema
from app.common.response import SuccessResponse
from app.core.dependencies import AuthPermission
from app.core.router_class import OperationLogRoute

from .service import LeaveRequestService

# leave模块路由器
LeaveRouter = APIRouter(
    route_class=OperationLogRoute, prefix="/leave-requests", tags=["请假管理"]
)


@LeaveRouter.get("/pending", summary="待审核请假", description="获取待审核的请假申请")
async def leave_requests_pending(
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:leave_request:list"])),
) -> JSONResponse:
    """待审核请假"""
    result = await LeaveRequestService.get_pending_service(auth)
    return SuccessResponse(data=result, msg="待审核请假获取成功")
