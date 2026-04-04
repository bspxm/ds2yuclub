"""
assessment模块 - 控制器
能力评估管理API
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from app.api.v1.module_system.auth.schema import AuthSchema
from app.common.response import SuccessResponse
from app.core.dependencies import AuthPermission
from app.core.router_class import OperationLogRoute

from ..student.schema import (
    AbilityAssessmentCreateSchema,
    AbilityAssessmentUpdateSchema,
    AbilityAssessmentQueryParam,
)
from ..student.service import AbilityAssessmentService

# assessment模块路由器
AssessmentRouter = APIRouter(
    route_class=OperationLogRoute, prefix="/assessments", tags=["能力评估管理"]
)


@AssessmentRouter.post("", summary="创建评估", description="创建学员能力评估")
async def assessment_create(
    data: AbilityAssessmentCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:assessment:create"])),
) -> JSONResponse:
    """创建评估"""
    result = await AbilityAssessmentService.create_service(auth, data)
    return SuccessResponse(data=result, msg="评估创建成功")


@AssessmentRouter.put(
    "/{assessment_id}", summary="更新评估", description="更新能力评估"
)
async def assessment_update(
    assessment_id: int,
    data: AbilityAssessmentUpdateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:assessment:update"])),
) -> JSONResponse:
    """更新评估"""
    result = await AbilityAssessmentService.update_service(auth, assessment_id, data)
    return SuccessResponse(data=result, msg="评估更新成功")


@AssessmentRouter.delete("", summary="删除评估", description="批量删除能力评估")
async def assessment_delete(
    data: list[int],
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:assessment:delete"])),
) -> JSONResponse:
    """删除评估"""
    result = await AbilityAssessmentService.delete_service(auth, data)
    return SuccessResponse(data=result, msg="评估删除成功")


@AssessmentRouter.get(
    "/student/{student_id}/latest",
    summary="最新评估",
    description="获取学员最新能力评估",
)
async def assessment_latest(
    student_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:assessment:list"])),
) -> JSONResponse:
    """最新评估"""
    result = await AbilityAssessmentService.get_latest_service(auth, student_id)
    if not result:
        return SuccessResponse(data=None, msg="该学员暂无评估记录")
    return SuccessResponse(data=result, msg="最新评估获取成功")


@AssessmentRouter.get(
    "/student/{student_id}/history",
    summary="评估历史",
    description="获取学员能力评估历史",
)
async def assessment_history(
    student_id: int,
    limit: int = Query(10, ge=1, le=50, description="返回记录数"),
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:assessment:list"])),
) -> JSONResponse:
    """评估历史"""
    result = await AbilityAssessmentService.get_history_service(auth, student_id, limit)
    return SuccessResponse(data=result, msg="评估历史获取成功")


@AssessmentRouter.get(
    "", summary="评估列表", description="获取能力评估列表（支持分页和查询）"
)
async def assessment_list(
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:assessment:list"])),
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    student_id: Optional[int] = Query(None, description="学员ID"),
    coach_id: Optional[int] = Query(None, description="教练ID"),
    min_overall_score: Optional[float] = Query(None, description="最小综合评分"),
    max_overall_score: Optional[float] = Query(None, description="最大综合评分"),
    assessment_date_start: Optional[str] = Query(None, description="评估开始日期"),
    assessment_date_end: Optional[str] = Query(None, description="评估结束日期"),
) -> JSONResponse:
    """评估列表"""
    search = AbilityAssessmentQueryParam(
        student_id=student_id,
        coach_id=coach_id,
        min_overall_score=min_overall_score,
        max_overall_score=max_overall_score,
        assessment_date_start=assessment_date_start,
        assessment_date_end=assessment_date_end,
    )
    result = await AbilityAssessmentService.page_service(
        auth, page_no, page_size, search
    )
    return SuccessResponse(data=result, msg="评估列表获取成功")
