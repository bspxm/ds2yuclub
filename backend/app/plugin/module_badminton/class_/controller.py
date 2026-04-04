"""
class_模块 - 控制器
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

from ..enums import ClassTypeEnum, ClassStatusEnum
from .schema import *
from .service import *

# class_模块路由器
Class_Router = APIRouter(
    route_class=OperationLogRoute, prefix="/class_", tags=["class_管理"]
)


@Class_Router.get(
    "/semester/{semester_id}", summary="学期班级", description="获取指定学期的所有班级"
)
async def classes_by_semester(
    semester_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class:list"])),
) -> JSONResponse:
    """学期班级"""
    result = await ClassService.get_by_semester_service(auth, semester_id)
    return SuccessResponse(data=result, msg="学期班级获取成功")


@Class_Router.get(
    "/{class_id}/available-time-slots",
    summary="班级可用时间段",
    description="获取班级的可用时间段，根据班级类型返回不同选择逻辑",
)
async def get_available_time_slots(
    class_id: int,
    redis: Redis = Depends(redis_getter),
    day_of_week: Optional[int] = Query(
        None, description="星期几（0=周日，1=周一，...，6=周六）"
    ),
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class:list"])),
) -> JSONResponse:
    """获取班级可用时间段"""
    from app.core.logger import logger

    logger.info(
        f"API接收参数: class_id={class_id}, day_of_week={day_of_week}, redis_type={type(redis).__name__}"
    )
    # 使用关键字参数调用，避免参数顺序问题
    result = await ClassService.get_available_time_slots(
        auth=auth, redis=redis, class_id=class_id, day_of_week=day_of_week
    )
    return SuccessResponse(data=result, msg="班级可用时间段获取成功")


# ============================================================================
# 班级管理 API
# ============================================================================


@Class_Router.post("/classes", summary="创建班级", description="创建新班级")
async def class_create(
    data: ClassCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class:create"])),
) -> JSONResponse:
    """创建班级"""
    result = await ClassService.create_service(auth, data)
    return SuccessResponse(data=result, msg="班级创建成功")


@Class_Router.get(
    "/classes", summary="班级列表", description="获取班级列表（支持分页和查询）"
)
async def class_list(
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class:list"])),
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    name: Optional[str] = Query(None, description="班级名称"),
    class_type: Optional[ClassTypeEnum] = Query(None, description="班级类型"),
    semester_id: Optional[int] = Query(None, description="学期ID"),
    status: Optional[ClassStatusEnum] = Query(None, description="班级状态"),
    coach_id: Optional[int] = Query(None, description="教练ID"),
) -> JSONResponse:
    """班级列表"""
    search = ClassQueryParam(
        name=name,
        class_type=class_type,
        semester_id=semester_id,
        status=status,
        coach_id=coach_id,
    )
    result = await ClassService.page_service(auth, page_no, page_size, search)
    return SuccessResponse(data=result, msg="班级列表获取成功")


@Class_Router.get("/classes/{id}", summary="班级详情", description="获取班级详细信息")
async def class_detail(
    id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class:detail"])),
) -> JSONResponse:
    """班级详情"""
    result = await ClassService.detail_service(auth, id)
    return SuccessResponse(data=result, msg="班级详情获取成功")


@Class_Router.put("/classes/{id}", summary="更新班级", description="更新班级信息")
async def class_update(
    id: int,
    data: ClassUpdateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class:update"])),
) -> JSONResponse:
    """更新班级"""
    result = await ClassService.update_service(auth, id, data)
    return SuccessResponse(data=result, msg="班级更新成功")


@Class_Router.delete("/classes", summary="删除班级", description="批量删除班级")
async def class_delete(
    ids: str = Query(..., description="班级ID列表，用逗号分隔"),
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class:delete"])),
) -> JSONResponse:
    """删除班级"""
    id_list = [int(id) for id in ids.split(",")]
    result = await ClassService.delete_service(auth, id_list)
    return SuccessResponse(data=result, msg="班级删除成功")


# ============================================================================
# 学期制课时结算系统 - 购买记录管理 API
# ============================================================================
