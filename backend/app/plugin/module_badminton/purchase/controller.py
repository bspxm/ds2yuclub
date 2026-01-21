"""
purchase模块 - 控制器
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

# purchase模块路由器
PurchaseRouter = APIRouter(
    route_class=OperationLogRoute,
    prefix="/purchases",
    tags=["purchase管理"]
)

@PurchaseRouter.get("/student/{student_id}", summary="学员购买记录", description="获取指定学员的所有购买记录")
async def purchases_by_student(
    student_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:purchase:list"]))
) -> JSONResponse:
    """学员购买记录"""
    result = await PurchaseService.get_by_student_service(auth, student_id)
    return SuccessResponse(data=result, msg="学员购买记录获取成功")


@PurchaseRouter.post("/batch", summary="批量创建购买记录", description="为多个学员批量创建购买记录")
async def batch_create_purchases(
    data: BatchPurchaseCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:purchase:create"]))
) -> JSONResponse:
    """批量创建购买记录"""
    result = await PurchaseService.batch_create_service(auth, data)
    return SuccessResponse(data=result, msg=result.get("message", "批量创建完成"))


# ============================================================================
# 学期制课时结算系统 - 考勤记录管理 API
# ============================================================================
