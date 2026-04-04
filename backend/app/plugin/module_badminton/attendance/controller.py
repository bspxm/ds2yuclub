"""
attendance模块 - 控制器
考勤记录管理API
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from app.api.v1.module_system.auth.schema import AuthSchema
from app.common.response import SuccessResponse
from app.core.dependencies import AuthPermission
from app.core.router_class import OperationLogRoute

from ..class_.schema import (
    ClassAttendanceCreateSchema,
    ClassAttendanceUpdateSchema,
    ClassAttendanceQueryParam,
)
from ..attendance.service import ClassAttendanceService
from ..enums import AttendanceStatusEnum

# attendance模块路由器
AttendanceRouter = APIRouter(
    route_class=OperationLogRoute, prefix="/class-attendances", tags=["考勤记录管理"]
)


@AttendanceRouter.post("", summary="创建考勤记录", description="创建新考勤记录")
async def class_attendance_create(
    data: ClassAttendanceCreateSchema,
    auth: AuthSchema = Depends(
        AuthPermission(["module_badminton:class_attendance:create"])
    ),
) -> JSONResponse:
    """创建考勤记录"""
    result = await ClassAttendanceService.create_service(auth, data)
    return SuccessResponse(data=result, msg="考勤记录创建成功")


@AttendanceRouter.get(
    "", summary="考勤记录列表", description="获取考勤记录列表（支持分页和查询）"
)
async def class_attendance_list(
    auth: AuthSchema = Depends(
        AuthPermission(["module_badminton:class_attendance:list"])
    ),
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    student_id: Optional[int] = Query(None, description="学员ID"),
    class_id: Optional[int] = Query(None, description="班级ID"),
    schedule_id: Optional[int] = Query(None, description="排课记录ID"),
    attendance_status: Optional[AttendanceStatusEnum] = Query(
        None, description="考勤状态"
    ),
    attendance_date_start: Optional[str] = Query(None, description="考勤日期范围-起始"),
    attendance_date_end: Optional[str] = Query(None, description="考勤日期范围-结束"),
) -> JSONResponse:
    """考勤记录列表"""
    search = ClassAttendanceQueryParam(
        student_id=student_id,
        class_id=class_id,
        schedule_id=schedule_id,
        attendance_status=attendance_status,
        attendance_date_start=attendance_date_start,
        attendance_date_end=attendance_date_end,
    )
    result = await ClassAttendanceService.page_service(auth, page_no, page_size, search)
    return SuccessResponse(data=result, msg="考勤记录列表获取成功")


@AttendanceRouter.get(
    "/{id}", summary="考勤记录详情", description="获取考勤记录详细信息"
)
async def class_attendance_detail(
    id: int,
    auth: AuthSchema = Depends(
        AuthPermission(["module_badminton:class_attendance:detail"])
    ),
) -> JSONResponse:
    """考勤记录详情"""
    result = await ClassAttendanceService.detail_service(auth, id)
    return SuccessResponse(data=result, msg="考勤记录详情获取成功")


@AttendanceRouter.put("/{id}", summary="更新考勤记录", description="更新考勤记录信息")
async def class_attendance_update(
    id: int,
    data: ClassAttendanceUpdateSchema,
    auth: AuthSchema = Depends(
        AuthPermission(["module_badminton:class_attendance:update"])
    ),
) -> JSONResponse:
    """更新考勤记录"""
    result = await ClassAttendanceService.update_service(auth, id, data)
    return SuccessResponse(data=result, msg="考勤记录更新成功")


@AttendanceRouter.delete("", summary="删除考勤记录", description="批量删除考勤记录")
async def class_attendance_delete(
    ids: str = Query(..., description="考勤记录ID列表，用逗号分隔"),
    auth: AuthSchema = Depends(
        AuthPermission(["module_badminton:class_attendance:delete"])
    ),
) -> JSONResponse:
    """删除考勤记录"""
    id_list = [int(id) for id in ids.split(",")]
    result = await ClassAttendanceService.delete_service(auth, id_list)
    return SuccessResponse(data=result, msg="考勤记录删除成功")


@AttendanceRouter.get(
    "/student/{student_id}",
    summary="学员考勤记录",
    description="获取指定学员的所有考勤记录",
)
async def class_attendances_by_student(
    student_id: int,
    auth: AuthSchema = Depends(
        AuthPermission(["module_badminton:class_attendance:list"])
    ),
) -> JSONResponse:
    """学员考勤记录"""
    result = await ClassAttendanceService.get_by_student_service(auth, student_id)
    return SuccessResponse(data=result, msg="学员考勤记录获取成功")


@AttendanceRouter.get(
    "/class/{class_id}",
    summary="班级考勤记录",
    description="获取指定班级的所有考勤记录",
)
async def class_attendances_by_class(
    class_id: int,
    auth: AuthSchema = Depends(
        AuthPermission(["module_badminton:class_attendance:list"])
    ),
) -> JSONResponse:
    """班级考勤记录"""
    result = await ClassAttendanceService.get_by_class_service(auth, class_id)
    return SuccessResponse(data=result, msg="班级考勤记录获取成功")
