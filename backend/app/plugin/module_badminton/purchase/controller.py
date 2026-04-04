"""
purchase模块 - 控制器
"""

from typing import Optional
from datetime import date
from redis.asyncio.client import Redis

from fastapi import APIRouter, Depends, Query, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse

from app.api.v1.module_system.auth.schema import AuthSchema
from app.common.response import SuccessResponse
from app.core.dependencies import AuthPermission, redis_getter
from app.core.exceptions import CustomException
from app.core.router_class import OperationLogRoute

from ..enums import PurchaseTypeEnum, PurchaseStatusEnum
from .schema import *
from .service import *

# purchase模块路由器
PurchaseRouter = APIRouter(
    route_class=OperationLogRoute, prefix="/purchases", tags=["purchase管理"]
)


@PurchaseRouter.get(
    "/student/{student_id}",
    summary="学员购买记录",
    description="获取指定学员的所有购买记录",
)
async def purchases_by_student(
    student_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:purchase:list"])),
) -> JSONResponse:
    """学员购买记录"""
    result = await PurchaseService.get_by_student_service(auth, student_id)
    return SuccessResponse(data=result, msg="学员购买记录获取成功")


@PurchaseRouter.post(
    "/batch", summary="批量创建购买记录", description="为多个学员批量创建购买记录"
)
async def batch_create_purchases(
    data: BatchPurchaseCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:purchase:create"])),
    redis: Redis = Depends(redis_getter),
) -> JSONResponse:
    """批量创建购买记录"""
    result = await PurchaseService.batch_create_service(
        auth=auth, redis=redis, data=data
    )
    return SuccessResponse(data=result, msg=result.get("message", "批量创建完成"))


# ============================================================================
# 购买记录管理 API
# ============================================================================


@PurchaseRouter.post("", summary="创建购买记录", description="创建新购买记录")
async def purchase_create(
    data: PurchaseCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:purchase:create"])),
    redis: Redis = Depends(redis_getter),
) -> JSONResponse:
    """创建购买记录"""
    result = await PurchaseService.create_service(auth=auth, redis=redis, data=data)
    return SuccessResponse(data=result, msg="购买记录创建成功")


@PurchaseRouter.get(
    "", summary="购买记录列表", description="获取购买记录列表（支持分页和查询）"
)
async def purchase_list(
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:purchase:list"])),
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    student_id: Optional[int] = Query(None, description="学员ID"),
    semester_id: Optional[int] = Query(None, description="学期ID"),
    class_id: Optional[int] = Query(None, description="班级ID"),
    purchase_type: Optional[PurchaseTypeEnum] = Query(None, description="购买类型"),
    status: Optional[PurchaseStatusEnum] = Query(None, description="购买状态"),
    purchase_date_start: Optional[str] = Query(None, description="购买日期范围-起始"),
    purchase_date_end: Optional[str] = Query(None, description="购买日期范围-结束"),
) -> JSONResponse:
    """购买记录列表"""
    search = PurchaseQueryParam(
        student_id=student_id,
        semester_id=semester_id,
        class_id=class_id,
        purchase_type=purchase_type,
        status=status,
        purchase_date_start=purchase_date_start,
        purchase_date_end=purchase_date_end,
    )
    result = await PurchaseService.page_service(auth, page_no, page_size, search)
    return SuccessResponse(data=result, msg="购买记录列表获取成功")


@PurchaseRouter.get("/{id}", summary="购买记录详情", description="获取购买记录详细信息")
async def purchase_detail(
    id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:purchase:detail"])),
) -> JSONResponse:
    """购买记录详情"""
    result = await PurchaseService.detail_service(auth, id)
    return SuccessResponse(data=result, msg="购买记录详情获取成功")


@PurchaseRouter.put("/{id}", summary="更新购买记录", description="更新购买记录信息")
async def purchase_update(
    id: int,
    data: PurchaseUpdateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:purchase:update"])),
    redis: Redis = Depends(redis_getter),
) -> JSONResponse:
    """更新购买记录"""
    result = await PurchaseService.update_service(
        auth=auth, redis=redis, purchase_id=id, data=data
    )
    return SuccessResponse(data=result, msg="购买记录更新成功")


@PurchaseRouter.delete("", summary="删除购买记录", description="批量删除购买记录")
async def purchase_delete(
    ids: str = Query(..., description="购买记录ID列表，用逗号分隔"),
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:purchase:delete"])),
) -> JSONResponse:
    """删除购买记录"""
    id_list = [int(id) for id in ids.split(",")]
    result = await PurchaseService.delete_service(auth, id_list)
    return SuccessResponse(data=result, msg="购买记录删除成功")


# ============================================================================
# 学期制课时结算系统 - 考勤记录管理 API
# ============================================================================
