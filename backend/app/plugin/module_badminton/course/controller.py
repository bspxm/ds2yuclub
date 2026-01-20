"""
course模块 - 控制器
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse

from app.api.v1.module_system.auth.schema import AuthSchema
from app.common.response import SuccessResponse
from app.core.dependencies import AuthPermission
from app.core.exceptions import CustomException
from app.core.router_class import OperationLogRoute

from .schema import *
from .service import *

# course模块路由器
CourseRouter = APIRouter(
    route_class=OperationLogRoute,
    prefix="/course",
    tags=["course管理"]
)

@CourseRouter.get("/upcoming", summary="近期课程", description="获取近期课程安排")
async def courses_upcoming(
    days: int = Query(7, ge=1, le=30, description="查询天数"),
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:course:list"]))
) -> JSONResponse:
    """近期课程"""
    result = await CourseService.get_upcoming_service(auth, days)
    return SuccessResponse(data=result, msg="近期课程获取成功")


# ============================================================================
# 请假管理 API
# ============================================================================
