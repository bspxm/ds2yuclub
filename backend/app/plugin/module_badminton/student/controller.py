"""
学员模块 - 控制器
学员管理、家长-学员关联管理API
"""

import io
from typing import Optional

from fastapi import APIRouter, Depends, Query, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse

from app.api.v1.module_system.auth.schema import AuthSchema
from app.common.response import SuccessResponse
from app.core.base_schema import BatchSetAvailable
from app.core.dependencies import AuthPermission
from app.core.exceptions import CustomException
from app.core.router_class import OperationLogRoute

from .service import StudentService, ParentStudentService, AbilityAssessmentService
from .schema import (
    StudentCreateSchema,
    StudentUpdateSchema,
    StudentQueryParam,
    ParentStudentCreateSchema,
)

# 学员管理路由器
StudentRouter = APIRouter(
    route_class=OperationLogRoute, prefix="/students", tags=["学员管理"]
)

# 家长-学员关联路由器
ParentStudentRouter = APIRouter(
    route_class=OperationLogRoute, prefix="/parent-student", tags=["家长-学员关联"]
)


# ============================================================================
# 学员管理 API
# ============================================================================


@StudentRouter.get("", summary="学员列表", description="获取学员列表（支持分页和查询）")
async def student_list(
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:student:list"])),
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    name: Optional[str] = Query(None, description="姓名（模糊查询）"),
    gender: Optional[str] = Query(None, description="性别"),
    group_name: Optional[str] = Query(None, description="所属组别"),
    campus: Optional[str] = Query(None, description="所属校区"),
    level: Optional[str] = Query(None, description="技术水平等级"),
) -> JSONResponse:
    """学员列表"""
    search = StudentQueryParam(
        name=name, gender=gender, group_name=group_name, campus=campus, level=level
    )
    result = await StudentService.page_service(auth, page_no, page_size, search)
    return SuccessResponse(data=result, msg="学员列表获取成功")


@StudentRouter.get(
    "/import-template", summary="下载导入模板", description="下载学员批量导入Excel模板"
)
async def student_import_template(
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:student:import"])),
) -> StreamingResponse:
    """下载导入模板"""
    excel_data = await StudentService.generate_import_template_service(auth)
    return StreamingResponse(
        io.BytesIO(excel_data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=student_import_template.xlsx"
        },
    )


@StudentRouter.post(
    "/import", summary="批量导入学员", description="通过Excel文件批量导入学员"
)
async def student_import(
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:student:import"])),
    file: UploadFile = File(..., description="Excel文件"),
) -> JSONResponse:
    """批量导入学员"""
    if not file.filename.endswith((".xlsx", ".xls")):
        raise CustomException(msg="仅支持Excel文件 (.xlsx, .xls)")

    # 读取文件内容
    content = await file.read()
    result = await StudentService.batch_import_service(auth, content)
    return SuccessResponse(data=result, msg="学员批量导入成功")


@StudentRouter.post("", summary="创建学员", description="创建新学员")
async def student_create(
    data: StudentCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:student:create"])),
) -> JSONResponse:
    """创建学员"""
    result = await StudentService.create_service(auth, data)
    return SuccessResponse(data=result, msg="学员创建成功")


@StudentRouter.post(
    "/batch-status", summary="批量设置状态", description="批量设置学员状态"
)
async def student_batch_status(
    data: BatchSetAvailable,
    auth: AuthSchema = Depends(
        AuthPermission(["module_badminton:student:batch_status"])
    ),
) -> JSONResponse:
    """批量设置状态"""
    result = await StudentService.batch_set_status_service(auth, data)
    return SuccessResponse(data=result, msg="状态更新成功")


@StudentRouter.delete("", summary="删除学员", description="批量删除学员")
async def student_delete(
    data: list[int],
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:student:delete"])),
) -> JSONResponse:
    """删除学员"""
    result = await StudentService.delete_service(auth, data)
    return SuccessResponse(data=result, msg="学员删除成功")


@StudentRouter.get("/{student_id}", summary="学员详情", description="获取学员详细信息")
async def student_detail(
    student_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:student:detail"])),
) -> JSONResponse:
    """学员详情"""
    result = await StudentService.detail_service(auth, student_id)
    return SuccessResponse(data=result, msg="学员详情获取成功")


@StudentRouter.put("/{student_id}", summary="更新学员", description="更新学员信息")
async def student_update(
    student_id: int,
    data: StudentUpdateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:student:update"])),
) -> JSONResponse:
    """更新学员"""
    result = await StudentService.update_service(auth, student_id, data)
    return SuccessResponse(data=result, msg="学员更新成功")


# ============================================================================
# 家长-学员关联 API
# ============================================================================


@ParentStudentRouter.post("", summary="创建关联", description="创建家长-学员关联")
async def parent_student_create(
    data: ParentStudentCreateSchema,
    auth: AuthSchema = Depends(
        AuthPermission(["module_badminton:parent_student:create"])
    ),
) -> JSONResponse:
    """创建关联"""
    result = await ParentStudentService.create_service(auth, data)
    return SuccessResponse(data=result, msg="关联创建成功")


@ParentStudentRouter.get(
    "/parent/{parent_id}",
    summary="获取家长的学员",
    description="获取家长关联的所有学员",
)
async def parent_student_by_parent(
    parent_id: int,
    auth: AuthSchema = Depends(
        AuthPermission(["module_badminton:parent_student:list"])
    ),
) -> JSONResponse:
    """获取家长的学员"""
    result = await ParentStudentService.get_by_parent_service(auth, parent_id)
    return SuccessResponse(data=result, msg="获取成功")


@ParentStudentRouter.get(
    "/student/{student_id}",
    summary="获取学员的家长",
    description="获取学员关联的所有家长",
)
async def parent_student_by_student(
    student_id: int,
    auth: AuthSchema = Depends(
        AuthPermission(["module_badminton:parent_student:list"])
    ),
) -> JSONResponse:
    """获取学员的家长"""
    result = await ParentStudentService.get_by_student_service(auth, student_id)
    return SuccessResponse(data=result, msg="获取成功")


@ParentStudentRouter.delete("", summary="删除关联", description="批量删除家长-学员关联")
async def parent_student_delete(
    data: list[int],
    auth: AuthSchema = Depends(
        AuthPermission(["module_badminton:parent_student:delete"])
    ),
) -> JSONResponse:
    """删除关联"""
    result = await ParentStudentService.delete_service(auth, data)
    return SuccessResponse(data=result, msg="关联删除成功")
