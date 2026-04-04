"""
semester模块 - 控制器
学期管理API
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from app.api.v1.module_system.auth.schema import AuthSchema
from app.common.response import SuccessResponse
from app.core.dependencies import AuthPermission
from app.core.router_class import OperationLogRoute

from .service import SemesterService
from .schema import SemesterCreateSchema, SemesterUpdateSchema, SemesterQueryParam
from ..enums import SemesterTypeEnum, SemesterStatusEnum

# semester模块路由器
SemesterRouter = APIRouter(
    route_class=OperationLogRoute, prefix="/semesters", tags=["学期管理"]
)


@SemesterRouter.post("", summary="创建学期", description="创建新学期")
async def semester_create(
    data: SemesterCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:semester:create"])),
) -> JSONResponse:
    """创建学期"""
    result = await SemesterService.create_service(auth, data)
    return SuccessResponse(data=result, msg="学期创建成功")


@SemesterRouter.get(
    "", summary="学期列表", description="获取学期列表（支持分页和查询）"
)
async def semester_list(
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:semester:list"])),
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    name: Optional[str] = Query(None, description="学期名称"),
    semester_type: Optional[SemesterTypeEnum] = Query(None, description="学期类型"),
    status: Optional[SemesterStatusEnum] = Query(None, description="学期状态"),
    start_date_start: Optional[str] = Query(None, description="开始日期范围-起始"),
    start_date_end: Optional[str] = Query(None, description="开始日期范围-结束"),
) -> JSONResponse:
    """学期列表"""
    search = SemesterQueryParam(
        name=name,
        semester_type=semester_type,
        status=status,
        start_date_start=start_date_start,
        start_date_end=start_date_end,
    )
    result = await SemesterService.page_service(auth, page_no, page_size, search)
    return SuccessResponse(data=result, msg="学期列表获取成功")


@SemesterRouter.get("/{id}", summary="学期详情", description="获取学期详细信息")
async def semester_detail(
    id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:semester:detail"])),
) -> JSONResponse:
    """学期详情"""
    result = await SemesterService.detail_service(auth, id)
    return SuccessResponse(data=result, msg="学期详情获取成功")


@SemesterRouter.put("/{id}", summary="更新学期", description="更新学期信息")
async def semester_update(
    id: int,
    data: SemesterUpdateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:semester:update"])),
) -> JSONResponse:
    """更新学期"""
    result = await SemesterService.update_service(auth, id, data)
    return SuccessResponse(data=result, msg="学期更新成功")


@SemesterRouter.delete("", summary="删除学期", description="批量删除学期")
async def semester_delete(
    ids: list[int],
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:semester:delete"])),
) -> JSONResponse:
    """删除学期"""
    result = await SemesterService.delete_service(auth, ids)
    return SuccessResponse(data=result, msg="学期删除成功")


@SemesterRouter.get("/current", summary="当前学期", description="获取当前活跃学期")
async def semester_current(
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:semester:list"])),
) -> JSONResponse:
    """当前学期"""
    result = await SemesterService.get_current_service(auth)
    return SuccessResponse(data=result, msg="当前学期获取成功")
