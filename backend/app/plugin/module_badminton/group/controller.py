"""
group模块 - Controller路由层
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from app.api.v1.module_system.auth.schema import AuthSchema
from app.common.response import SuccessResponse
from app.core.dependencies import AuthPermission
from app.core.exceptions import CustomException
from app.core.router_class import OperationLogRoute

from .schema import (
    AbilityGroupCreateSchema,
    AbilityGroupUpdateSchema,
    AbilityGroupQueryParam
)
from .service import AbilityGroupService

# 能力分组路由器
AbilityGroupRouter = APIRouter(
    route_class=OperationLogRoute,
    prefix="/groups",
    tags=["能力分组管理"]
)


# ============================================================================
# 能力分组管理路由
# ============================================================================

@AbilityGroupRouter.get("", summary="分组列表", description="获取分组列表（支持分页和查询）")
async def list_groups(
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:group:list"])),
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    name: Optional[str] = Query(None, description="分组名称（模糊查询）"),
    coach_id: Optional[int] = Query(None, description="教练ID"),
    student_id: Optional[int] = Query(None, description="学员ID"),
    created_time: Optional[list[str]] = Query(None, description="创建时间范围"),
    updated_time: Optional[list[str]] = Query(None, description="更新时间范围"),
    created_id: Optional[int] = Query(None, description="创建人ID"),
    updated_id: Optional[int] = Query(None, description="更新人ID"),
) -> JSONResponse:
    """分组列表"""
    search = AbilityGroupQueryParam(
        name=name,
        coach_id=coach_id,
        student_id=student_id,
        created_time=created_time,
        updated_time=updated_time,
        created_id=created_id,
        updated_id=updated_id
    )
    result = await AbilityGroupService.page_service(auth, page_no, page_size, search=search)
    return SuccessResponse(data=result, msg="分组列表获取成功")


@AbilityGroupRouter.get("/{group_id}", summary="分组详情", description="获取分组详情")
async def get_group_detail(
    group_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:group:list"]))
) -> JSONResponse:
    """分组详情"""
    result = await AbilityGroupService.detail_service(auth, group_id)
    return SuccessResponse(data=result, msg="分组详情获取成功")


@AbilityGroupRouter.post("", summary="创建分组", description="创建新分组")
async def create_group(
    data: AbilityGroupCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:group:create"]))
) -> JSONResponse:
    """创建分组"""
    result = await AbilityGroupService.create_service(auth, data)
    return SuccessResponse(data=result, msg="分组创建成功")


@AbilityGroupRouter.put("/{group_id}", summary="更新分组", description="更新分组信息")
async def update_group(
    group_id: int,
    data: AbilityGroupUpdateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:group:update"]))
) -> JSONResponse:
    """更新分组"""
    result = await AbilityGroupService.update_service(auth, group_id, data)
    return SuccessResponse(data=result, msg="分组更新成功")


@AbilityGroupRouter.delete("", summary="删除分组", description="删除分组（批量）")
async def delete_groups(
    ids: list[int],
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:group:delete"]))
) -> JSONResponse:
    """删除分组"""
    result = await AbilityGroupService.delete_service(auth, ids)
    return SuccessResponse(data=result, msg="分组删除成功")


@AbilityGroupRouter.get("/meta/coaches", summary="获取教练列表", description="获取角色为教练的用户列表")
async def get_coaches(
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:group:list"]))
) -> JSONResponse:
    """获取教练列表"""
    result = await AbilityGroupService.get_coaches_service(auth)
    return SuccessResponse(data=result, msg="教练列表获取成功")


@AbilityGroupRouter.get("/meta/available-students", summary="获取可用学员", description="获取未分组或可重新分组的学员列表")
async def get_available_students(
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:group:list"])),
    exclude_group_id: Optional[int] = Query(None, description="排除的分组ID（用于编辑时排除当前分组的学员）")
) -> JSONResponse:
    """获取可用学员"""
    result = await AbilityGroupService.get_available_students_service(auth, exclude_group_id=exclude_group_id)
    return SuccessResponse(data=result, msg="可用学员列表获取成功")