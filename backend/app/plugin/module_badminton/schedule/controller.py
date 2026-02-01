"""
schedule模块 - 控制器
"""

from typing import Optional, List
from datetime import date

from fastapi import APIRouter, Depends, Query, Body
from fastapi.responses import JSONResponse
from redis.asyncio.client import Redis

from app.api.v1.module_system.auth.schema import AuthSchema
from app.common.response import SuccessResponse
from app.core.dependencies import AuthPermission, redis_getter
from app.core.router_class import OperationLogRoute

from ..class_.schema import (
    ClassScheduleCreateV2Schema,
    AvailableStudentSchema,
    ClassScheduleQueryParam
)
from .service import ClassScheduleService

# schedule模块路由器
ClassScheduleRouter = APIRouter(
    route_class=OperationLogRoute,
    prefix="/class-schedules",
    tags=["排课管理"]
)

@ClassScheduleRouter.get("", summary="排课记录列表", description="获取排课记录列表（分页）")
async def list_schedule(
    page_no: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    class_id: Optional[int] = Query(None, description="班级ID"),
    schedule_date_start: Optional[str] = Query(None, description="开始日期"),
    schedule_date_end: Optional[str] = Query(None, description="结束日期"),
    schedule_status: Optional[str] = Query(None, description="状态"),
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class-schedule:list"]))
) -> JSONResponse:
    """排课记录列表"""
    # 构建查询参数
    search = ClassScheduleQueryParam(
        class_id=class_id,
        schedule_date_start=schedule_date_start,
        schedule_date_end=schedule_date_end,
        schedule_status=schedule_status
    )
    
    result = await ClassScheduleService.page_service(auth, page_no, page_size, search)
    return SuccessResponse(data=result, msg="排课记录列表获取成功")

@ClassScheduleRouter.get("/available-students", summary="获取可用学员列表", description="根据学期、日期、时间段获取可用学员")
async def get_available_students(
    semester_id: int = Query(..., description="学期ID"),
    schedule_date: date = Query(..., description="排课日期"),
    time_slot_ids: str = Query(..., description="时间段ID列表（逗号分隔）"),
    class_ids: Optional[str] = Query(None, description="班级ID列表（逗号分隔）"),
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class-schedule:list"])),
    redis: Redis = Depends(redis_getter)
) -> JSONResponse:
    """获取可用学员列表"""
    # 解析逗号分隔的参数
    time_slot_id_list = [int(x) for x in time_slot_ids.split(',')]
    class_id_list = [int(x) for x in class_ids.split(',')] if class_ids else None

    result = await ClassScheduleService.get_available_students_service(
        auth=auth,
        redis=redis,
        semester_id=semester_id,
        schedule_date=schedule_date,
        time_slot_ids=time_slot_id_list,
        class_ids=class_id_list
    )
    return SuccessResponse(data=result, msg="可用学员列表获取成功")

@ClassScheduleRouter.post("/v2", summary="创建排课记录(V2)", description="创建排课记录，支持学员选择和自动创建考勤")
async def create_schedule_v2(
    data: ClassScheduleCreateV2Schema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class-schedule:add"])),
    redis: Redis = Depends(redis_getter)
) -> JSONResponse:
    """创建排课记录(V2)"""
    result = await ClassScheduleService.create_v2_service(auth, redis, data)
    return SuccessResponse(data=result, msg="排课记录创建成功")

@ClassScheduleRouter.get("/{id}", summary="排课记录详情", description="获取排课记录详情")
async def get_schedule(
    id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class-schedule:list"]))
) -> JSONResponse:
    """排课记录详情"""
    result = await ClassScheduleService.detail_service(auth, id)
    return SuccessResponse(data=result, msg="排课记录详情获取成功")

@ClassScheduleRouter.put("/{id}", summary="更新排课记录", description="更新排课记录")
async def update_schedule(
    id: int,
    data: ClassScheduleCreateV2Schema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class-schedule:edit"])),
    redis: Redis = Depends(redis_getter)
) -> JSONResponse:
    """更新排课记录"""
    result = await ClassScheduleService.update_service(auth, redis, id, data)
    return SuccessResponse(data=result, msg="排课记录更新成功")

@ClassScheduleRouter.delete("", summary="删除排课记录", description="批量删除排课记录")
async def delete_schedule(
    ids: str = Query(..., description="ID列表（逗号分隔）"),
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class-schedule:remove"]))
) -> JSONResponse:
    """删除排课记录"""
    id_list = [int(x) for x in ids.split(',')]
    result = await ClassScheduleService.delete_service(auth, id_list)
    return SuccessResponse(data=result, msg="排课记录删除成功")

@ClassScheduleRouter.get("/class/{class_id}", summary="指定班级的排课记录", description="获取指定班级的所有排课记录")
async def get_class_schedules(
    class_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class-schedule:list"]))
) -> JSONResponse:
    """指定班级的排课记录"""
    # 构造查询参数
    search = {"class_id": ("eq", class_id)}
    result = await ClassScheduleService.list_service(auth, search)
    return SuccessResponse(data=result, msg="班级排课记录获取成功")

@ClassScheduleRouter.get("/class/{class_id}/upcoming", summary="指定班级的近期排课", description="获取指定班级的即将上课排课记录")
async def get_upcoming_schedules(
    class_id: int,
    days: int = Query(7, description="查询天数"),
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class-schedule:list"]))
) -> JSONResponse:
    """指定班级的近期排课"""
    # 构造日期范围查询
    from datetime import datetime, timedelta
    start_date = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    
    search = {
        "class_id": ("eq", class_id),
        "schedule_date": ("between", (start_date, end_date))
    }
    # 按日期升序
    order_by = [{"schedule_date": "asc"}, {"start_time": "asc"}]
    
    result = await ClassScheduleService.list_service(auth, search, order_by)
    return SuccessResponse(data=result, msg="近期排课记录获取成功")
