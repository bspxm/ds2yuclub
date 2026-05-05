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

from ..team.schema import (
    ClassScheduleCreateV2Schema,
    AvailableStudentSchema,
    ClassScheduleQueryParam,
)
from .service import ClassScheduleService

# schedule模块路由器
ClassScheduleRouter = APIRouter(
    route_class=OperationLogRoute, prefix="/class-schedules", tags=["排课管理"]
)


@ClassScheduleRouter.get(
    "", summary="排课记录列表", description="获取排课记录列表（分页）"
)
async def list_schedule(
    page_no: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    class_id: Optional[int] = Query(None, description="班级ID"),
    schedule_date_start: Optional[str] = Query(None, description="开始日期"),
    schedule_date_end: Optional[str] = Query(None, description="结束日期"),
    schedule_status: Optional[str] = Query(None, description="状态"),
    auth: AuthSchema = Depends(
        AuthPermission(["module_badminton:class-schedule:list"])
    ),
) -> JSONResponse:
    """排课记录列表"""
    # 构建查询参数
    search = ClassScheduleQueryParam(
        class_id=class_id,
        schedule_date_start=schedule_date_start,
        schedule_date_end=schedule_date_end,
        schedule_status=schedule_status,
    )

    result = await ClassScheduleService.page_service(auth, page_no, page_size, search)
    return SuccessResponse(data=result, msg="排课记录列表获取成功")


@ClassScheduleRouter.post(
    "/v2",
    summary="创建排课记录(V2)",
    description="创建排课记录，支持学员选择和自动创建考勤",
)
async def create_schedule_v2(
    data: ClassScheduleCreateV2Schema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class-schedule:add"])),
    redis: Redis = Depends(redis_getter),
) -> JSONResponse:
    """创建排课记录(V2)"""
    result = await ClassScheduleService.create_v2_service(auth, redis, data)
    return SuccessResponse(data=result, msg="排课记录创建成功")


@ClassScheduleRouter.get(
    "/available-students",
    summary="获取可用学员列表",
    description="获取可排课的学员列表（根据课时包配置筛选）",
)
async def get_available_students(
    semester_id: int = Query(..., description="学期ID"),
    schedule_date: str = Query(..., description="排课日期（YYYY-MM-DD格式）"),
    time_slots: str = Query(..., description="时间段JSON配置（JSON字符串格式）"),
    class_ids: Optional[str] = Query(
        None,
        description="班级ID列表（逗号分隔，可选，如果未提供则查询该学期下所有班级）",
    ),
    auth: AuthSchema = Depends(
        AuthPermission(["module_badminton:class-schedule:list"])
    ),
    redis: Redis = Depends(redis_getter),
) -> JSONResponse:
    """
    获取可用学员列表

    筛选逻辑：
    1. 查询指定班级（如果未提供则查询该学期下所有班级）的购买记录
    2. 筛选 selected_time_slots 包含任一时间段代码的购买记录
    3. 检查学员是否有剩余课时
    4. 检查排课日期是否在购买记录的有效期内
    5. 返回符合条件的学员列表
    """
    import json
    from datetime import datetime

    # 解析日期
    try:
        parsed_date = datetime.strptime(schedule_date, "%Y-%m-%d").date()
    except ValueError:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=400, detail="日期格式错误，请使用YYYY-MM-DD格式"
        )

    # 解析时间段JSON
    try:
        time_slots_dict = json.loads(time_slots)
    except json.JSONDecodeError:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=400, detail="时间段配置格式错误，请使用JSON格式"
        )

    # 解析班级ID列表（如果提供）
    class_ids_list = None
    if class_ids:
        try:
            class_ids_list = [int(x.strip()) for x in class_ids.split(",")]
        except ValueError:
            from fastapi import HTTPException

            raise HTTPException(
                status_code=400, detail="班级ID格式错误，请使用逗号分隔的数字"
            )

    result = await ClassScheduleService.get_available_students_service(
        auth=auth,
        redis=redis,
        semester_id=semester_id,
        schedule_date=parsed_date,
        time_slots=time_slots_dict,
        class_ids=class_ids_list,
    )
    return JSONResponse(
        content={
            "code": 0,
            "msg": "可用学员列表获取成功",
            "data": result,
            "success": True,
        }
    )


@ClassScheduleRouter.get(
    "/{id}", summary="排课记录详情", description="获取排课记录详情"
)
async def get_schedule(
    id: int,
    auth: AuthSchema = Depends(
        AuthPermission(["module_badminton:class-schedule:list"])
    ),
    redis: Redis = Depends(redis_getter),
) -> JSONResponse:
    """排课记录详情"""
    result = await ClassScheduleService.detail_service(auth, redis, id)
    return SuccessResponse(data=result, msg="排课记录详情获取成功")


@ClassScheduleRouter.put("/{id}", summary="更新排课记录", description="更新排课记录")
async def update_schedule(
    id: int,
    data: ClassScheduleCreateV2Schema,
    auth: AuthSchema = Depends(
        AuthPermission(["module_badminton:class-schedule:edit"])
    ),
    redis: Redis = Depends(redis_getter),
) -> JSONResponse:
    """更新排课记录"""
    result = await ClassScheduleService.update_service(auth, redis, id, data)
    return SuccessResponse(data=result, msg="排课记录更新成功")


@ClassScheduleRouter.delete("", summary="删除排课记录", description="批量删除排课记录")
async def delete_schedule(
    ids: str = Query(..., description="ID列表（逗号分隔）"),
    auth: AuthSchema = Depends(
        AuthPermission(["module_badminton:class-schedule:remove"])
    ),
) -> JSONResponse:
    """删除排课记录"""
    id_list = [int(x) for x in ids.split(",")]
    result = await ClassScheduleService.delete_service(auth, id_list)
    return SuccessResponse(data=result, msg="排课记录删除成功")


@ClassScheduleRouter.get(
    "/team/{class_id}",
    summary="指定班级的排课记录",
    description="获取指定班级的所有排课记录",
)
async def get_class_schedules(
    class_id: int,
    auth: AuthSchema = Depends(
        AuthPermission(["module_badminton:class-schedule:list"])
    ),
) -> JSONResponse:
    """指定班级的排课记录"""
    # 构造查询参数
    search = {"class_id": ("eq", class_id)}
    result = await ClassScheduleService.list_service(auth, search)
    return SuccessResponse(data=result, msg="班级排课记录获取成功")


@ClassScheduleRouter.get(
    "/team/{class_id}/upcoming",
    summary="指定班级的近期排课",
    description="获取指定班级的即将上课排课记录",
)
async def get_upcoming_schedules(
    class_id: int,
    days: int = Query(7, description="查询天数"),
    auth: AuthSchema = Depends(
        AuthPermission(["module_badminton:class-schedule:list"])
    ),
) -> JSONResponse:
    """指定班级的近期排课"""
    # 构造日期范围查询
    from datetime import datetime, timedelta

    start_date = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

    search = {
        "class_id": ("eq", class_id),
        "schedule_date": ("between", (start_date, end_date)),
    }
    # 按日期升序
    order_by = [{"schedule_date": "asc"}, {"start_time": "asc"}]

    result = await ClassScheduleService.list_service(auth, search, order_by)
    return SuccessResponse(data=result, msg="近期排课记录获取成功")


@ClassScheduleRouter.get(
    "/coach/daily",
    summary="教练每日排课",
    description="获取教练在指定日期的排课列表（按时间段分组）",
)
async def get_coach_daily_schedule(
    coach_id: int = Query(..., description="教练ID"),
    schedule_date: str = Query(..., description="排课日期"),
    auth: AuthSchema = Depends(
        AuthPermission(["module_badminton:class-schedule:list"])
    ),
    redis: Redis = Depends(redis_getter),
) -> JSONResponse:
    """教练每日排课"""
    result = await ClassScheduleService.get_coach_daily_schedule_service(
        auth, redis, coach_id, schedule_date
    )
    return SuccessResponse(data=result, msg="教练每日排课获取成功")
