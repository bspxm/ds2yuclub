# 羽毛球模块控制器重构实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 `module_badminton/controller.py` 中的路由分散到各个子模块的 `controller.py` 中，保持向后兼容性。

**Architecture:** 采用自注册机制，每个子模块的 `controller.py` 定义自己的 `APIRouter` 实例，系统自动发现并注册。主 `controller.py` 简化为只保留健康检查和模块信息端点。

**Tech Stack:** FastAPI, Python 3.x, 自动路由发现机制

---

## 文件结构

### 需要修改的文件：
- `backend/app/plugin/module_badminton/controller.py` - 简化，只保留健康检查
- `backend/app/plugin/module_badminton/student/controller.py` - 添加学员管理API
- `backend/app/plugin/module_badminton/tournament/controller.py` - 添加赛事管理API
- `backend/app/plugin/module_badminton/course/controller.py` - 添加课程管理API
- `backend/app/plugin/module_badminton/semester/controller.py` - 添加学期管理API
- `backend/app/plugin/module_badminton/class_/controller.py` - 添加班级管理API
- `backend/app/plugin/module_badminton/purchase/controller.py` - 添加购买记录API
- `backend/app/plugin/module_badminton/schedule/controller.py` - 添加排课记录API

### 需要创建的文件：
- `backend/app/plugin/module_badminton/assessment/controller.py` - 能力评估API
- `backend/app/plugin/module_badminton/leave/controller.py` - 请假管理API
- `backend/app/plugin/module_badminton/attendance/controller.py` - 考勤记录API

---

## Task 1: 创建 assessment/controller.py - 能力评估API

**Files:**
- Create: `backend/app/plugin/module_badminton/assessment/controller.py`

- [ ] **Step 1: 创建 assessment/controller.py 文件**

```python
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
    AbilityAssessmentQueryParam
)
from ..student.service import AbilityAssessmentService

# assessment模块路由器
AssessmentRouter = APIRouter(
    route_class=OperationLogRoute,
    prefix="/assessments",
    tags=["能力评估管理"]
)


@AssessmentRouter.post(
    "",
    summary="创建评估",
    description="创建学员能力评估"
)
async def assessment_create(
    data: AbilityAssessmentCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:assessment:create"])),
) -> JSONResponse:
    """创建评估"""
    result = await AbilityAssessmentService.create_service(auth, data)
    return SuccessResponse(data=result, msg="评估创建成功")


@AssessmentRouter.put(
    "/{assessment_id}",
    summary="更新评估",
    description="更新能力评估"
)
async def assessment_update(
    assessment_id: int,
    data: AbilityAssessmentUpdateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:assessment:update"])),
) -> JSONResponse:
    """更新评估"""
    result = await AbilityAssessmentService.update_service(auth, assessment_id, data)
    return SuccessResponse(data=result, msg="评估更新成功")


@AssessmentRouter.delete(
    "",
    summary="删除评估",
    description="批量删除能力评估"
)
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
    description="获取学员最新能力评估"
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
    description="获取学员能力评估历史"
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
    "",
    summary="评估列表",
    description="获取能力评估列表（支持分页和查询）"
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
```

- [ ] **Step 2: 创建 assessment/__init__.py 文件**

```python
from .controller import AssessmentRouter

__all__ = ["AssessmentRouter"]
```

---

## Task 2: 创建 leave/controller.py - 请假管理API

**Files:**
- Create: `backend/app/plugin/module_badminton/leave/controller.py`

- [ ] **Step 1: 创建 leave/controller.py 文件**

```python
"""
leave模块 - 控制器
请假管理API
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.v1.module_system.auth.schema import AuthSchema
from app.common.response import SuccessResponse
from app.core.dependencies import AuthPermission
from app.core.router_class import OperationLogRoute

from .service import LeaveRequestService

# leave模块路由器
LeaveRouter = APIRouter(
    route_class=OperationLogRoute,
    prefix="/leave-requests",
    tags=["请假管理"]
)


@LeaveRouter.get(
    "/pending",
    summary="待审核请假",
    description="获取待审核的请假申请"
)
async def leave_requests_pending(
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:leave_request:list"])),
) -> JSONResponse:
    """待审核请假"""
    result = await LeaveRequestService.get_pending_service(auth)
    return SuccessResponse(data=result, msg="待审核请假获取成功")
```

- [ ] **Step 2: 创建 leave/__init__.py 文件（如果不存在）**

检查文件是否存在，如果不存在则创建：

```python
from .model import LeaveRequestModel
from .service import LeaveRequestService

__all__ = ["LeaveRequestModel", "LeaveRequestService"]
```

---

## Task 3: 创建 attendance/controller.py - 考勤记录API

**Files:**
- Create: `backend/app/plugin/module_badminton/attendance/controller.py`

- [ ] **Step 1: 创建 attendance/controller.py 文件**

```python
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
    ClassAttendanceQueryParam
)
from ..attendance.service import ClassAttendanceService
from ..enums import AttendanceStatusEnum

# attendance模块路由器
AttendanceRouter = APIRouter(
    route_class=OperationLogRoute,
    prefix="/class-attendances",
    tags=["考勤记录管理"]
)


@AttendanceRouter.post(
    "",
    summary="创建考勤记录",
    description="创建新考勤记录"
)
async def class_attendance_create(
    data: ClassAttendanceCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class_attendance:create"])),
) -> JSONResponse:
    """创建考勤记录"""
    result = await ClassAttendanceService.create_service(auth, data)
    return SuccessResponse(data=result, msg="考勤记录创建成功")


@AttendanceRouter.get(
    "",
    summary="考勤记录列表",
    description="获取考勤记录列表（支持分页和查询）"
)
async def class_attendance_list(
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class_attendance:list"])),
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    student_id: Optional[int] = Query(None, description="学员ID"),
    class_id: Optional[int] = Query(None, description="班级ID"),
    schedule_id: Optional[int] = Query(None, description="排课记录ID"),
    attendance_status: Optional[AttendanceStatusEnum] = Query(None, description="考勤状态"),
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
    "/{id}",
    summary="考勤记录详情",
    description="获取考勤记录详细信息"
)
async def class_attendance_detail(
    id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class_attendance:detail"])),
) -> JSONResponse:
    """考勤记录详情"""
    result = await ClassAttendanceService.detail_service(auth, id)
    return SuccessResponse(data=result, msg="考勤记录详情获取成功")


@AttendanceRouter.put(
    "/{id}",
    summary="更新考勤记录",
    description="更新考勤记录信息"
)
async def class_attendance_update(
    id: int,
    data: ClassAttendanceUpdateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class_attendance:update"])),
) -> JSONResponse:
    """更新考勤记录"""
    result = await ClassAttendanceService.update_service(auth, id, data)
    return SuccessResponse(data=result, msg="考勤记录更新成功")


@AttendanceRouter.delete(
    "",
    summary="删除考勤记录",
    description="批量删除考勤记录"
)
async def class_attendance_delete(
    ids: str = Query(..., description="考勤记录ID列表，用逗号分隔"),
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class_attendance:delete"])),
) -> JSONResponse:
    """删除考勤记录"""
    id_list = [int(id) for id in ids.split(",")]
    result = await ClassAttendanceService.delete_service(auth, id_list)
    return SuccessResponse(data=result, msg="考勤记录删除成功")


@AttendanceRouter.get(
    "/student/{student_id}",
    summary="学员考勤记录",
    description="获取指定学员的所有考勤记录"
)
async def class_attendances_by_student(
    student_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class_attendance:list"])),
) -> JSONResponse:
    """学员考勤记录"""
    result = await ClassAttendanceService.get_by_student_service(auth, student_id)
    return SuccessResponse(data=result, msg="学员考勤记录获取成功")


@AttendanceRouter.get(
    "/class/{class_id}",
    summary="班级考勤记录",
    description="获取指定班级的所有考勤记录"
)
async def class_attendances_by_class(
    class_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class_attendance:list"])),
) -> JSONResponse:
    """班级考勤记录"""
    result = await ClassAttendanceService.get_by_class_service(auth, class_id)
    return SuccessResponse(data=result, msg="班级考勤记录获取成功")
```

- [ ] **Step 2: 创建 attendance/__init__.py 文件（如果不存在）**

```python
from .model import ClassAttendanceModel
from .service import ClassAttendanceService

__all__ = ["ClassAttendanceModel", "ClassAttendanceService"]
```

---

## Task 4: 重构 student/controller.py - 添加学员管理API

**Files:**
- Modify: `backend/app/plugin/module_badminton/student/controller.py`

- [ ] **Step 1: 完整重写 student/controller.py 文件**

```python
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
    route_class=OperationLogRoute,
    prefix="/students",
    tags=["学员管理"]
)

# 家长-学员关联路由器
ParentStudentRouter = APIRouter(
    route_class=OperationLogRoute,
    prefix="/parent-student",
    tags=["家长-学员关联"]
)


# ============================================================================
# 学员管理 API
# ============================================================================


@StudentRouter.get(
    "",
    summary="学员列表",
    description="获取学员列表（支持分页和查询）"
)
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
    "/import-template",
    summary="下载导入模板",
    description="下载学员批量导入Excel模板"
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
    "/import",
    summary="批量导入学员",
    description="通过Excel文件批量导入学员"
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


@StudentRouter.post(
    "",
    summary="创建学员",
    description="创建新学员"
)
async def student_create(
    data: StudentCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:student:create"])),
) -> JSONResponse:
    """创建学员"""
    result = await StudentService.create_service(auth, data)
    return SuccessResponse(data=result, msg="学员创建成功")


@StudentRouter.post(
    "/batch-status",
    summary="批量设置状态",
    description="批量设置学员状态"
)
async def student_batch_status(
    data: BatchSetAvailable,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:student:batch_status"])),
) -> JSONResponse:
    """批量设置状态"""
    result = await StudentService.batch_set_status_service(auth, data)
    return SuccessResponse(data=result, msg="状态更新成功")


@StudentRouter.delete(
    "",
    summary="删除学员",
    description="批量删除学员"
)
async def student_delete(
    data: list[int],
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:student:delete"])),
) -> JSONResponse:
    """删除学员"""
    result = await StudentService.delete_service(auth, data)
    return SuccessResponse(data=result, msg="学员删除成功")


@StudentRouter.get(
    "/{student_id}",
    summary="学员详情",
    description="获取学员详细信息"
)
async def student_detail(
    student_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:student:detail"])),
) -> JSONResponse:
    """学员详情"""
    result = await StudentService.detail_service(auth, student_id)
    return SuccessResponse(data=result, msg="学员详情获取成功")


@StudentRouter.put(
    "/{student_id}",
    summary="更新学员",
    description="更新学员信息"
)
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


@ParentStudentRouter.post(
    "",
    summary="创建关联",
    description="创建家长-学员关联"
)
async def parent_student_create(
    data: ParentStudentCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:parent_student:create"])),
) -> JSONResponse:
    """创建关联"""
    result = await ParentStudentService.create_service(auth, data)
    return SuccessResponse(data=result, msg="关联创建成功")


@ParentStudentRouter.get(
    "/parent/{parent_id}",
    summary="获取家长的学员",
    description="获取家长关联的所有学员"
)
async def parent_student_by_parent(
    parent_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:parent_student:list"])),
) -> JSONResponse:
    """获取家长的学员"""
    result = await ParentStudentService.get_by_parent_service(auth, parent_id)
    return SuccessResponse(data=result, msg="获取成功")


@ParentStudentRouter.get(
    "/student/{student_id}",
    summary="获取学员的家长",
    description="获取学员关联的所有家长"
)
async def parent_student_by_student(
    student_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:parent_student:list"])),
) -> JSONResponse:
    """获取学员的家长"""
    result = await ParentStudentService.get_by_student_service(auth, student_id)
    return SuccessResponse(data=result, msg="获取成功")


@ParentStudentRouter.delete(
    "",
    summary="删除关联",
    description="批量删除家长-学员关联"
)
async def parent_student_delete(
    data: list[int],
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:parent_student:delete"])),
) -> JSONResponse:
    """删除关联"""
    result = await ParentStudentService.delete_service(auth, data)
    return SuccessResponse(data=result, msg="关联删除成功")
```

---

## Task 5: 重构 tournament/controller.py - 添加赛事管理API

**Files:**
- Modify: `backend/app/plugin/module_badminton/tournament/controller.py`

- [ ] **Step 1: 在 tournament/controller.py 文件开头添加赛事管理API**

在现有的 `TournamentRouter` 定义之后，添加以下路由：

```python
# 在文件开头的导入部分添加
from .schema import (
    TournamentCreateSchema,
    TournamentUpdateSchema,
    MatchScoreSchema,
)


# 在 TournamentRouter 定义之后添加赛事管理API

@TournamentRouter.post(
    "",
    summary="创建赛事",
    description="创建新赛事"
)
async def tournament_create(
    data: TournamentCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:create"])),
) -> JSONResponse:
    """创建赛事"""
    result = await TournamentService.create_service(auth, data)
    return SuccessResponse(data=result, msg="赛事创建成功")


@TournamentRouter.get(
    "",
    summary="赛事列表",
    description="获取赛事列表"
)
async def tournament_list(
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:list"])),
) -> JSONResponse:
    """赛事列表"""
    result = await TournamentService.list_service(auth)
    return SuccessResponse(data=result, msg="赛事列表获取成功")


@TournamentRouter.get(
    "/active",
    summary="进行中赛事",
    description="获取进行中的赛事"
)
async def tournament_active(
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:list"])),
) -> JSONResponse:
    """进行中赛事"""
    result = await TournamentService.get_active_service(auth)
    return SuccessResponse(data=result, msg="进行中赛事获取成功")


@TournamentRouter.delete(
    "",
    summary="删除赛事",
    description="批量删除赛事"
)
async def tournament_delete(
    data: list[int],
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:delete"])),
) -> JSONResponse:
    """删除赛事"""
    await TournamentService.delete_service(auth, data)
    return SuccessResponse(msg="赛事删除成功")
```

---

## Task 6: 重构 course/controller.py - 添加课程管理API

**Files:**
- Modify: `backend/app/plugin/module_badminton/course/controller.py`

- [ ] **Step 1: 完整重写 course/controller.py 文件**

```python
"""
course模块 - 控制器
课程管理API
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse

from app.api.v1.module_system.auth.schema import AuthSchema
from app.common.response import SuccessResponse
from app.core.dependencies import AuthPermission
from app.core.exceptions import CustomException
from app.core.router_class import OperationLogRoute

from .schema import CourseCreateSchema
from .service import CourseService

# course模块路由器
CourseRouter = APIRouter(
    route_class=OperationLogRoute,
    prefix="/courses",
    tags=["课程管理"]
)


@CourseRouter.get(
    "/upcoming",
    summary="近期课程",
    description="获取近期课程安排"
)
async def courses_upcoming(
    days: int = Query(7, ge=1, le=30, description="查询天数"),
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:course:list"])),
) -> JSONResponse:
    """近期课程"""
    result = await CourseService.get_upcoming_service(auth, days)
    return SuccessResponse(data=result, msg="近期课程获取成功")


@CourseRouter.post(
    "/schedule",
    summary="创建课程（排课）",
    description="创建新课程安排"
)
async def course_schedule(
    data: CourseCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:course:create"])),
) -> JSONResponse:
    """创建课程（排课）"""
    result = await CourseService.schedule_service(auth, data.model_dump())
    return SuccessResponse(data=result, msg="课程创建成功")
```

---

## Task 7: 重构 semester/controller.py - 添加学期管理API

**Files:**
- Modify: `backend/app/plugin/module_badminton/semester/controller.py`

- [ ] **Step 1: 完整重写 semester/controller.py 文件**

```python
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
    route_class=OperationLogRoute,
    prefix="/semesters",
    tags=["学期管理"]
)


@SemesterRouter.post(
    "",
    summary="创建学期",
    description="创建新学期"
)
async def semester_create(
    data: SemesterCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:semester:create"])),
) -> JSONResponse:
    """创建学期"""
    result = await SemesterService.create_service(auth, data)
    return SuccessResponse(data=result, msg="学期创建成功")


@SemesterRouter.get(
    "",
    summary="学期列表",
    description="获取学期列表（支持分页和查询）"
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


@SemesterRouter.get(
    "/{id}",
    summary="学期详情",
    description="获取学期详细信息"
)
async def semester_detail(
    id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:semester:detail"])),
) -> JSONResponse:
    """学期详情"""
    result = await SemesterService.detail_service(auth, id)
    return SuccessResponse(data=result, msg="学期详情获取成功")


@SemesterRouter.put(
    "/{id}",
    summary="更新学期",
    description="更新学期信息"
)
async def semester_update(
    id: int,
    data: SemesterUpdateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:semester:update"])),
) -> JSONResponse:
    """更新学期"""
    result = await SemesterService.update_service(auth, id, data)
    return SuccessResponse(data=result, msg="学期更新成功")


@SemesterRouter.delete(
    "",
    summary="删除学期",
    description="批量删除学期"
)
async def semester_delete(
    ids: list[int],
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:semester:delete"])),
) -> JSONResponse:
    """删除学期"""
    result = await SemesterService.delete_service(auth, ids)
    return SuccessResponse(data=result, msg="学期删除成功")


@SemesterRouter.get(
    "/current",
    summary="当前学期",
    description="获取当前活跃学期"
)
async def semester_current(
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:semester:list"])),
) -> JSONResponse:
    """当前学期"""
    result = await SemesterService.get_current_service(auth)
    return SuccessResponse(data=result, msg="当前学期获取成功")
```

---

## Task 8: 重构 class_/controller.py - 添加班级管理API

**Files:**
- Modify: `backend/app/plugin/module_badminton/class_/controller.py`

- [ ] **Step 1: 完整重写 class_/controller.py 文件**

查看现有文件内容，保留已有的路由，并添加班级管理相关的API。

---

## Task 9: 重构 purchase/controller.py - 添加购买记录API

**Files:**
- Modify: `backend/app/plugin/module_badminton/purchase/controller.py`

- [ ] **Step 1: 完整重写 purchase/controller.py 文件**

查看现有文件内容，保留已有的路由，并添加购买记录相关的API。

---

## Task 10: 重构 schedule/controller.py - 添加排课记录API

**Files:**
- Modify: `backend/app/plugin/module_badminton/schedule/controller.py`

- [ ] **Step 1: 检查现有 schedule/controller.py 文件**

查看现有文件内容，确认是否需要添加更多路由。

---

## Task 11: 简化主 controller.py - 只保留健康检查和模块信息

**Files:**
- Modify: `backend/app/plugin/module_badminton/controller.py`

- [ ] **Step 1: 简化主 controller.py 文件**

```python
"""
羽毛球培训会员管理系统 - 主控制器

路由自动注册规则：
- 模块目录: module_badminton
- 路由前缀: /badminton
- 自动发现所有controller.py文件中的APIRouter实例

注意：所有业务API已分散到各个子模块的controller.py中
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.common.response import SuccessResponse
from app.core.router_class import OperationLogRoute

# 主路由器 - 自动注册为/badminton路由
BadmintonRouter = APIRouter(
    route_class=OperationLogRoute, prefix="", tags=["羽毛球培训会员管理"]
)


@BadmintonRouter.get(
    "/health", summary="健康检查", description="检查羽毛球模块是否正常运行"
)
async def health_check() -> JSONResponse:
    """健康检查端点"""
    return SuccessResponse(
        data={"module": "badminton", "status": "healthy"}, msg="羽毛球模块运行正常"
    )


@BadmintonRouter.get("/info", summary="模块信息", description="获取羽毛球模块信息")
async def module_info() -> JSONResponse:
    """模块信息"""
    info = {
        "name": "羽毛球培训会员管理系统",
        "version": "1.0.0",
        "description": "羽毛球培训会员管理系统，包含学员管理、比赛管理、课程管理等功能",
        "features": [
            "学员档案管理",
            "家长-学员关联管理",
            "能力评估系统（9项能力评分）",
            "比赛管理（4种赛制支持）",
            "课程预约与排课系统",
            "手机号/微信登录",
        ],
        "modules": [
            "student - 学员管理",
            "assessment - 能力评估",
            "tournament - 赛事管理",
            "course - 课程管理",
            "leave - 请假管理",
            "semester - 学期管理",
            "class_ - 班级管理",
            "purchase - 购买记录",
            "attendance - 考勤记录",
            "schedule - 排课记录",
        ],
    }
    return SuccessResponse(data=info, msg="模块信息获取成功")


@BadmintonRouter.get(
    "/tournament/types",
    summary="获取支持的赛制类型",
    description="获取系统支持的比赛赛制类型",
)
async def get_tournament_types() -> JSONResponse:
    """获取赛制类型"""
    from .tournament.engine import TournamentType

    types = [
        {
            "value": TournamentType.ROUND_ROBIN.value,
            "label": "分组循环赛（带淘汰赛）",
            "description": "小组循环赛 + 交叉淘汰赛，保证多场比赛机会",
        },
        {
            "value": TournamentType.PURE_GROUP.value,
            "label": "纯小组赛",
            "description": "仅小组循环赛决定名次，适合快速排位",
        },
        {
            "value": TournamentType.PROMOTION_RELEGATION.value,
            "label": "定区升降赛",
            "description": "位置挑战赛，趣味性强，位置实时变动",
        },
        {
            "value": TournamentType.SINGLE_ELIMINATION.value,
            "label": "小组单败制淘汰赛",
            "description": "循环赛确定种子排名 + 淘汰赛决出所有名次",
        },
    ]
    return SuccessResponse(data=types, msg="赛制类型获取成功")
```

---

## Task 12: 验证所有路由正确注册

**Files:**
- None (验证步骤)

- [ ] **Step 1: 运行后端服务，检查路由注册**

```bash
cd /home/filter/myproject/ds2yuclub/backend
python main.py run --env=dev
```

检查启动日志，确认所有路由正确注册：
- ✅ 注册容器: /badminton (路由数: X)
- 确认所有子模块的 controller.py 被正确发现

- [ ] **Step 2: 测试健康检查端点**

```bash
curl http://localhost:8000/badminton/health
```

预期响应：
```json
{
  "code": 0,
  "msg": "羽毛球模块运行正常",
  "data": {
    "module": "badminton",
    "status": "healthy"
  }
}
```

- [ ] **Step 3: 测试模块信息端点**

```bash
curl http://localhost:8000/badminton/info
```

预期响应包含模块列表。

---

## 执行顺序

按照以下顺序执行任务：
1. Task 1: 创建 assessment/controller.py
2. Task 2: 创建 leave/controller.py
3. Task 3: 创建 attendance/controller.py
4. Task 4: 重构 student/controller.py
5. Task 5: 重构 tournament/controller.py
6. Task 6: 重构 course/controller.py
7. Task 7: 重构 semester/controller.py
8. Task 8: 重构 class_/controller.py
9. Task 9: 重构 purchase/controller.py
10. Task 10: 重构 schedule/controller.py
11. Task 11: 简化主 controller.py
12. Task 12: 验证所有路由正确注册

---

## 注意事项

1. **向后兼容性**：保持 `crud.py`, `schema.py`, `service.py`, `model.py` 作为重新导出文件，确保现有代码不受影响。

2. **路由前缀**：每个子模块的 `APIRouter` 需要定义正确的 `prefix`，避免路由冲突。

3. **权限标识**：保持权限标识不变，确保现有权限配置继续有效。

4. **导入路径**：使用相对导入（`from ..module import`）访问其他模块的内容。

5. **测试**：重构完成后，需要测试所有API端点，确保功能正常。