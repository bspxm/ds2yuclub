"""
羽毛球培训会员管理系统 - 主控制器

路由自动注册规则：
- 模块目录: module_badminton
- 路由前缀: /badminton
- 自动发现所有controller.py文件中的APIRouter实例
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

from .enums import SemesterTypeEnum, SemesterStatusEnum, ClassTypeEnum, ClassStatusEnum, PurchaseTypeEnum, PurchaseStatusEnum, AttendanceStatusEnum, ScheduleStatusEnum

from .schema import (
    StudentCreateSchema,
    StudentUpdateSchema,
    StudentQueryParam,
    ParentStudentCreateSchema,
    AbilityAssessmentCreateSchema,
    AbilityAssessmentUpdateSchema,
    AbilityAssessmentQueryParam,
    TournamentCreateSchema,
    CourseCreateSchema,
    SemesterCreateSchema,
    SemesterUpdateSchema,
    SemesterQueryParam,
    ClassCreateSchema,
    ClassUpdateSchema,
    ClassQueryParam,
    PurchaseCreateSchema,
    PurchaseUpdateSchema,
    PurchaseQueryParam,
    ClassAttendanceCreateSchema,
    ClassAttendanceUpdateSchema,
    ClassAttendanceQueryParam,
    ClassScheduleCreateSchema,
    ClassScheduleUpdateSchema,
    ClassScheduleQueryParam
)
from .service import (
    StudentService,
    ParentStudentService,
    AbilityAssessmentService,
    TournamentService,
    CourseService,
    LeaveRequestService,
    SemesterService,
    ClassService,
    PurchaseService,
    ClassAttendanceService,
    ClassScheduleService
)

# 主路由器 - 自动注册为/badminton路由
BadmintonRouter = APIRouter(
    route_class=OperationLogRoute,
    prefix="",
    tags=["羽毛球培训会员管理"]
)



@BadmintonRouter.get("/health", summary="健康检查", description="检查羽毛球模块是否正常运行")
async def health_check() -> JSONResponse:
    """健康检查端点"""
    return SuccessResponse(data={"module": "badminton", "status": "healthy"}, msg="羽毛球模块运行正常")

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
            "手机号/微信登录"
        ]
    }
    return SuccessResponse(data=info, msg="模块信息获取成功")

@BadmintonRouter.get("/tournament/types", summary="获取支持的赛制类型", description="获取系统支持的比赛赛制类型")
async def get_tournament_types() -> JSONResponse:
    """获取赛制类型"""
    from .tournament.engine import TournamentType
    
    types = [
        {
            "value": TournamentType.ROUND_ROBIN.value,
            "label": "分组循环赛（带淘汰赛）",
            "description": "小组循环赛 + 交叉淘汰赛，保证多场比赛机会"
        },
        {
            "value": TournamentType.PURE_GROUP.value,
            "label": "纯小组赛",
            "description": "仅小组循环赛决定名次，适合快速排位"
        },
        {
            "value": TournamentType.PROMOTION_RELEGATION.value,
            "label": "定区升降赛",
            "description": "位置挑战赛，趣味性强，位置实时变动"
        },
        {
            "value": TournamentType.SINGLE_ELIMINATION.value,
            "label": "小组单败制淘汰赛",
            "description": "循环赛确定种子排名 + 淘汰赛决出所有名次"
        }
    ]
    return SuccessResponse(data=types, msg="赛制类型获取成功")

@BadmintonRouter.post("/tournament/simulate", summary="模拟比赛", description="模拟分组循环赛比赛")
async def simulate_tournament(
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:simulate"]))
) -> JSONResponse:
    """模拟比赛（测试用）"""
    try:
        from .tournament.engine import TournamentEngineFactory, TournamentType, TournamentConfig, MatchFormat
        from .tournament.round_robin import RoundRobinEngine
        
        # 创建测试参赛者
        participants = []
        for i in range(8):
            participants.append({
                "id": i + 1,
                "name": f"选手{i+1}",
                "seed_rank": i + 1 if i < 4 else None
            })
        
        # 创建引擎
        config = TournamentConfig(
            tournament_type=TournamentType.ROUND_ROBIN,
            match_format=MatchFormat.BEST_OF_THREE_21,
            group_size=4,
            num_groups=2,
            advance_from_group=2
        )
        
        engine = RoundRobinEngine(config)
        
        # 创建分组
        from .tournament.engine import Participant
        participant_objs = [Participant(**p) for p in participants]
        groups = engine.create_groups(participant_objs)
        
        # 生成比赛
        matches = engine.generate_matches(groups)
        
        # 模拟比赛结果
        import random
        for match in matches:
            if match.status == "scheduled":
                match.winner_id = random.choice([match.player1_id, match.player2_id])
                match.status = "completed"
        
        # 计算排名
        rankings = engine.calculate_rankings(groups, matches)
        
        result = {
            "groups": [
                {
                    "id": group.id,
                    "name": group.name,
                    "participants": [{"id": p.id, "name": p.name} for p in group.participants]
                }
                for group in groups
            ],
            "matches": [
                {
                    "id": match.id,
                    "player1": match.player1_name,
                    "player2": match.player2_name,
                    "winner": match.winner_id
                }
                for match in matches if match.status == "completed"
            ],
            "rankings": {
                group_id: [{"id": p.id, "name": p.name} for p in rank_list]
                for group_id, rank_list in rankings.items()
            }
        }
        
        return SuccessResponse(data=result, msg="比赛模拟成功")
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"code": 500, "msg": f"模拟失败: {str(e)}", "data": None}
        )


# ============================================================================
# 学员管理 API
# ============================================================================

@BadmintonRouter.get("/students", summary="学员列表", description="获取学员列表（支持分页和查询）")
async def student_list(
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:student:list"])),
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    name: Optional[str] = Query(None, description="姓名（模糊查询）"),
    gender: Optional[str] = Query(None, description="性别"),
    group_name: Optional[str] = Query(None, description="所属组别"),
    campus: Optional[str] = Query(None, description="所属校区"),
    level: Optional[str] = Query(None, description="技术水平等级")
) -> JSONResponse:
    """学员列表"""
    search = StudentQueryParam(
        name=name,
        gender=gender,
        group_name=group_name,
        campus=campus,
        level=level
    )
    result = await StudentService.page_service(auth, page_no, page_size, search)
    return SuccessResponse(data=result, msg="学员列表获取成功")

@BadmintonRouter.get("/students/import-template", summary="下载导入模板", description="下载学员批量导入Excel模板")
async def student_import_template(
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:student:import"]))
) -> StreamingResponse:
    """下载导入模板"""
    excel_data = await StudentService.generate_import_template_service(auth)
    return StreamingResponse(
        io.BytesIO(excel_data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=student_import_template.xlsx"}
    )

@BadmintonRouter.post("/students/import", summary="批量导入学员", description="通过Excel文件批量导入学员")
async def student_import(
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:student:import"])),
    file: UploadFile = File(..., description="Excel文件")
) -> JSONResponse:
    """批量导入学员"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise CustomException(msg="仅支持Excel文件 (.xlsx, .xls)")
    
    # 读取文件内容
    content = await file.read()
    result = await StudentService.batch_import_service(auth, content)
    return SuccessResponse(data=result, msg="学员批量导入成功")

@BadmintonRouter.post("/students", summary="创建学员", description="创建新学员")
async def student_create(
    data: StudentCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:student:create"]))
) -> JSONResponse:
    """创建学员"""
    result = await StudentService.create_service(auth, data)
    return SuccessResponse(data=result, msg="学员创建成功")

@BadmintonRouter.post("/students/batch-status", summary="批量设置状态", description="批量设置学员状态")
async def student_batch_status(
    data: BatchSetAvailable,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:student:batch_status"]))
) -> JSONResponse:
    """批量设置状态"""
    result = await StudentService.batch_set_status_service(auth, data)
    return SuccessResponse(data=result, msg="状态更新成功")

@BadmintonRouter.delete("/students", summary="删除学员", description="批量删除学员")
async def student_delete(
    data: list[int],
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:student:delete"]))
) -> JSONResponse:
    """删除学员"""
    result = await StudentService.delete_service(auth, data)
    return SuccessResponse(data=result, msg="学员删除成功")

@BadmintonRouter.get("/students/{student_id}", summary="学员详情", description="获取学员详细信息")
async def student_detail(
    student_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:student:detail"]))
) -> JSONResponse:
    """学员详情"""
    result = await StudentService.detail_service(auth, student_id)
    return SuccessResponse(data=result, msg="学员详情获取成功")

@BadmintonRouter.put("/students/{student_id}", summary="更新学员", description="更新学员信息")
async def student_update(
    student_id: int,
    data: StudentUpdateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:student:update"]))
) -> JSONResponse:
    """更新学员"""
    result = await StudentService.update_service(auth, student_id, data)
    return SuccessResponse(data=result, msg="学员更新成功")


# ============================================================================
# 家长-学员关联 API
# ============================================================================

@BadmintonRouter.post("/parent-student", summary="创建关联", description="创建家长-学员关联")
async def parent_student_create(
    data: ParentStudentCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:parent_student:create"]))
) -> JSONResponse:
    """创建关联"""
    result = await ParentStudentService.create_service(auth, data)
    return SuccessResponse(data=result, msg="关联创建成功")

@BadmintonRouter.get("/parent-student/parent/{parent_id}", summary="获取家长的学员", description="获取家长关联的所有学员")
async def parent_student_by_parent(
    parent_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:parent_student:list"]))
) -> JSONResponse:
    """获取家长的学员"""
    result = await ParentStudentService.get_by_parent_service(auth, parent_id)
    return SuccessResponse(data=result, msg="获取成功")

@BadmintonRouter.get("/parent-student/student/{student_id}", summary="获取学员的家长", description="获取学员关联的所有家长")
async def parent_student_by_student(
    student_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:parent_student:list"]))
) -> JSONResponse:
    """获取学员的家长"""
    result = await ParentStudentService.get_by_student_service(auth, student_id)
    return SuccessResponse(data=result, msg="获取成功")

@BadmintonRouter.delete("/parent-student", summary="删除关联", description="批量删除家长-学员关联")
async def parent_student_delete(
    data: list[int],
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:parent_student:delete"]))
) -> JSONResponse:
    """删除关联"""
    result = await ParentStudentService.delete_service(auth, data)
    return SuccessResponse(data=result, msg="关联删除成功")


# ============================================================================
# 能力评估 API
# ============================================================================

@BadmintonRouter.post("/assessments", summary="创建评估", description="创建学员能力评估")
async def assessment_create(
    data: AbilityAssessmentCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:assessment:create"]))
) -> JSONResponse:
    """创建评估"""
    result = await AbilityAssessmentService.create_service(auth, data)
    return SuccessResponse(data=result, msg="评估创建成功")

@BadmintonRouter.put("/assessments/{assessment_id}", summary="更新评估", description="更新能力评估")
async def assessment_update(
    assessment_id: int,
    data: AbilityAssessmentUpdateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:assessment:update"]))
) -> JSONResponse:
    """更新评估"""
    result = await AbilityAssessmentService.update_service(auth, assessment_id, data)
    return SuccessResponse(data=result, msg="评估更新成功")

@BadmintonRouter.delete("/assessments", summary="删除评估", description="批量删除能力评估")
async def assessment_delete(
    data: list[int],
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:assessment:delete"]))
) -> JSONResponse:
    """删除评估"""
    result = await AbilityAssessmentService.delete_service(auth, data)
    return SuccessResponse(data=result, msg="评估删除成功")

@BadmintonRouter.get("/assessments/student/{student_id}/latest", summary="最新评估", description="获取学员最新能力评估")
async def assessment_latest(
    student_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:assessment:list"]))
) -> JSONResponse:
    """最新评估"""
    result = await AbilityAssessmentService.get_latest_service(auth, student_id)
    if not result:
        return SuccessResponse(data=None, msg="该学员暂无评估记录")
    return SuccessResponse(data=result, msg="最新评估获取成功")

@BadmintonRouter.get("/assessments/student/{student_id}/history", summary="评估历史", description="获取学员能力评估历史")
async def assessment_history(
    student_id: int,
    limit: int = Query(10, ge=1, le=50, description="返回记录数"),
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:assessment:list"]))
) -> JSONResponse:
    """评估历史"""
    result = await AbilityAssessmentService.get_history_service(auth, student_id, limit)
    return SuccessResponse(data=result, msg="评估历史获取成功")

@BadmintonRouter.get("/assessments", summary="评估列表", description="获取能力评估列表（支持分页和查询）")
async def assessment_list(
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:assessment:list"])),
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    student_id: Optional[int] = Query(None, description="学员ID"),
    coach_id: Optional[int] = Query(None, description="教练ID"),
    min_overall_score: Optional[float] = Query(None, description="最小综合评分"),
    max_overall_score: Optional[float] = Query(None, description="最大综合评分"),
    assessment_date_start: Optional[str] = Query(None, description="评估开始日期"),
    assessment_date_end: Optional[str] = Query(None, description="评估结束日期")
) -> JSONResponse:
    """评估列表"""
    search = AbilityAssessmentQueryParam(
        student_id=student_id,
        coach_id=coach_id,
        min_overall_score=min_overall_score,
        max_overall_score=max_overall_score,
        assessment_date_start=assessment_date_start,
        assessment_date_end=assessment_date_end
    )
    result = await AbilityAssessmentService.page_service(auth, page_no, page_size, search)
    return SuccessResponse(data=result, msg="评估列表获取成功")


# ============================================================================
# 赛事管理 API
# ============================================================================

@BadmintonRouter.post("/tournaments", summary="创建赛事", description="创建新赛事")
async def tournament_create(
    data: TournamentCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:create"]))
) -> JSONResponse:
    """创建赛事"""
    result = await TournamentService.create_service(auth, data)
    return SuccessResponse(data=result, msg="赛事创建成功")

@BadmintonRouter.get("/tournaments", summary="赛事列表", description="获取赛事列表")
async def tournament_list(
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:list"]))
) -> JSONResponse:
    """赛事列表"""
    result = await TournamentService.list_service(auth)
    return SuccessResponse(data=result, msg="赛事列表获取成功")

@BadmintonRouter.get("/tournaments/active", summary="进行中赛事", description="获取进行中的赛事")
async def tournament_active(
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:list"]))
) -> JSONResponse:
    """进行中赛事"""
    result = await TournamentService.get_active_service(auth)
    return SuccessResponse(data=result, msg="进行中赛事获取成功")


# ============================================================================
# 参赛管理 API
# ============================================================================

@BadmintonRouter.post("/tournaments/{tournament_id}/register", summary="报名参赛", description="学员报名参加赛事")
async def tournament_register(
    tournament_id: int,
    student_id: int = Query(..., description="学员ID"),
    seed_rank: Optional[int] = Query(None, description="种子排名"),
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:register"]))
) -> JSONResponse:
    """报名参赛"""
    return SuccessResponse(data=result, msg="报名成功")

@BadmintonRouter.post("/tournaments/participants/{participant_id}/withdraw", summary="退赛", description="学员退赛")
async def tournament_withdraw(
    participant_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:withdraw"]))
) -> JSONResponse:
    """退赛"""
    return SuccessResponse(data=result, msg="退赛成功")

@BadmintonRouter.get("/tournaments/{tournament_id}/participants", summary="参赛者列表", description="获取赛事所有参赛者")
async def tournament_participants(
    tournament_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:participants"]))
) -> JSONResponse:
    """参赛者列表"""
    return SuccessResponse(data=result, msg="参赛者列表获取成功")


# ============================================================================
# 课程管理 API
# ============================================================================

@BadmintonRouter.get("/course/upcoming", summary="近期课程", description="获取近期课程安排")
async def course_upcoming(
    days: int = Query(7, ge=1, le=30, description="查询天数"),
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:course:list"]))
) -> JSONResponse:
    """近期课程"""
    result = await CourseService.get_upcoming_service(auth, days)
    return SuccessResponse(data=result, msg="近期课程获取成功")

@BadmintonRouter.post("/courses/schedule", summary="创建课程（排课）", description="创建新课程安排")
async def course_schedule(
    data: CourseCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:course:create"]))
) -> JSONResponse:
    """创建课程（排课）"""
    result = await CourseService.schedule_service(auth, data.model_dump())
    return SuccessResponse(data=result, msg="课程创建成功")

@BadmintonRouter.get("/leave-requests/pending", summary="待审核请假", description="获取待审核的请假申请")
async def leave_requests_pending(
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:leave_request:list"]))
) -> JSONResponse:
    """待审核请假"""
    result = await LeaveRequestService.get_pending_service(auth)
    return SuccessResponse(data=result, msg="待审核请假获取成功")


# ============================================================================
# 学期制课时结算系统 - 学期管理 API
# ============================================================================

@BadmintonRouter.post("/semesters", summary="创建学期", description="创建新学期")
async def semester_create(
    data: SemesterCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:semester:create"]))
) -> JSONResponse:
    """创建学期"""
    result = await SemesterService.create_service(auth, data)
    return SuccessResponse(data=result, msg="学期创建成功")

@BadmintonRouter.get("/semesters", summary="学期列表", description="获取学期列表（支持分页和查询）")
async def semester_list(
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:semester:list"])),
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    name: Optional[str] = Query(None, description="学期名称"),
    semester_type: Optional[SemesterTypeEnum] = Query(None, description="学期类型"),
    status: Optional[SemesterStatusEnum] = Query(None, description="学期状态"),
    start_date_start: Optional[str] = Query(None, description="开始日期范围-起始"),
    start_date_end: Optional[str] = Query(None, description="开始日期范围-结束")
) -> JSONResponse:
    """学期列表"""
    search = SemesterQueryParam(
        name=name,
        semester_type=semester_type,
        status=status,
        start_date_start=start_date_start,
        start_date_end=start_date_end
    )
    result = await SemesterService.page_service(auth, page_no, page_size, search)
    return SuccessResponse(data=result, msg="学期列表获取成功")

@BadmintonRouter.get("/semesters/{id}", summary="学期详情", description="获取学期详细信息")
async def semester_detail(
    id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:semester:detail"]))
) -> JSONResponse:
    """学期详情"""
    result = await SemesterService.detail_service(auth, id)
    return SuccessResponse(data=result, msg="学期详情获取成功")

@BadmintonRouter.put("/semesters/{id}", summary="更新学期", description="更新学期信息")
async def semester_update(
    id: int,
    data: SemesterUpdateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:semester:update"]))
) -> JSONResponse:
    """更新学期"""
    result = await SemesterService.update_service(auth, id, data)
    return SuccessResponse(data=result, msg="学期更新成功")

@BadmintonRouter.delete("/semesters", summary="删除学期", description="批量删除学期")
async def semester_delete(
    ids: list[int],
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:semester:delete"]))
) -> JSONResponse:
    """删除学期"""
    result = await SemesterService.delete_service(auth, ids)
    return SuccessResponse(data=result, msg="学期删除成功")

@BadmintonRouter.get("/semesters/current", summary="当前学期", description="获取当前活跃学期")
async def semester_current(
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:semester:list"]))
) -> JSONResponse:
    """当前学期"""
    result = await SemesterService.get_current_service(auth)
    return SuccessResponse(data=result, msg="当前学期获取成功")


# ============================================================================
# 学期制课时结算系统 - 班级管理 API
# ============================================================================

@BadmintonRouter.post("/classes", summary="创建班级", description="创建新班级")
async def class_create(
    data: ClassCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class:create"]))
) -> JSONResponse:
    """创建班级"""
    result = await ClassService.create_service(auth, data)
    return SuccessResponse(data=result, msg="班级创建成功")

@BadmintonRouter.get("/classes", summary="班级列表", description="获取班级列表（支持分页和查询）")
async def class_list(
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class:list"])),
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    name: Optional[str] = Query(None, description="班级名称"),
    class_type: Optional[ClassTypeEnum] = Query(None, description="班级类型"),
    semester_id: Optional[int] = Query(None, description="学期ID"),
    status: Optional[ClassStatusEnum] = Query(None, description="班级状态"),
    coach_id: Optional[int] = Query(None, description="教练ID")
) -> JSONResponse:
    """班级列表"""
    search = ClassQueryParam(
        name=name,
        class_type=class_type,
        semester_id=semester_id,
        status=status,
        coach_id=coach_id
    )
    result = await ClassService.page_service(auth, page_no, page_size, search)
    return SuccessResponse(data=result, msg="班级列表获取成功")

@BadmintonRouter.get("/classes/{id}", summary="班级详情", description="获取班级详细信息")
async def class_detail(
    id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class:detail"]))
) -> JSONResponse:
    """班级详情"""
    result = await ClassService.detail_service(auth, id)
    return SuccessResponse(data=result, msg="班级详情获取成功")

@BadmintonRouter.put("/classes/{id}", summary="更新班级", description="更新班级信息")
async def class_update(
    id: int,
    data: ClassUpdateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class:update"]))
) -> JSONResponse:
    """更新班级"""
    result = await ClassService.update_service(auth, id, data)
    return SuccessResponse(data=result, msg="班级更新成功")

@BadmintonRouter.delete("/classes", summary="删除班级", description="批量删除班级")
async def class_delete(
    ids: str = Query(..., description="班级ID列表，用逗号分隔"),
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class:delete"]))
) -> JSONResponse:
    """删除班级"""
    id_list = [int(id) for id in ids.split(",")]
    result = await ClassService.delete_service(auth, id_list)
    return SuccessResponse(data=result, msg="班级删除成功")

@BadmintonRouter.post("/purchases", summary="创建购买记录", description="创建新购买记录")
async def purchase_create(
    data: PurchaseCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:purchase:create"]))
) -> JSONResponse:
    """创建购买记录"""
    result = await PurchaseService.create_service(auth, data)
    return SuccessResponse(data=result, msg="购买记录创建成功")

@BadmintonRouter.get("/purchases", summary="购买记录列表", description="获取购买记录列表（支持分页和查询）")
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
    purchase_date_end: Optional[str] = Query(None, description="购买日期范围-结束")
) -> JSONResponse:
    """购买记录列表"""
    search = PurchaseQueryParam(
        student_id=student_id,
        semester_id=semester_id,
        class_id=class_id,
        purchase_type=purchase_type,
        status=status,
        purchase_date_start=purchase_date_start,
        purchase_date_end=purchase_date_end
    )
    result = await PurchaseService.page_service(auth, page_no, page_size, search)
    return SuccessResponse(data=result, msg="购买记录列表获取成功")

@BadmintonRouter.get("/purchases/{id}", summary="购买记录详情", description="获取购买记录详细信息")
async def purchase_detail(
    id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:purchase:detail"]))
) -> JSONResponse:
    """购买记录详情"""
    result = await PurchaseService.detail_service(auth, id)
    return SuccessResponse(data=result, msg="购买记录详情获取成功")

@BadmintonRouter.put("/purchases/{id}", summary="更新购买记录", description="更新购买记录信息")
async def purchase_update(
    id: int,
    data: PurchaseUpdateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:purchase:update"]))
) -> JSONResponse:
    """更新购买记录"""
    result = await PurchaseService.update_service(auth, id, data)
    return SuccessResponse(data=result, msg="购买记录更新成功")

@BadmintonRouter.delete("/purchases", summary="删除购买记录", description="批量删除购买记录")
async def purchase_delete(
    ids: str = Query(..., description="购买记录ID列表，用逗号分隔"),
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:purchase:delete"]))
) -> JSONResponse:
    """删除购买记录"""
    id_list = [int(id) for id in ids.split(",")]
    result = await PurchaseService.delete_service(auth, id_list)
    return SuccessResponse(data=result, msg="购买记录删除成功")

@BadmintonRouter.post("/class-attendances", summary="创建考勤记录", description="创建新考勤记录")
async def class_attendance_create(
    data: ClassAttendanceCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class_attendance:create"]))
) -> JSONResponse:
    """创建考勤记录"""
    result = await ClassAttendanceService.create_service(auth, data)
    return SuccessResponse(data=result, msg="考勤记录创建成功")

@BadmintonRouter.get("/class-attendances", summary="考勤记录列表", description="获取考勤记录列表（支持分页和查询）")
async def class_attendance_list(
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class_attendance:list"])),
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    student_id: Optional[int] = Query(None, description="学员ID"),
    class_id: Optional[int] = Query(None, description="班级ID"),
    schedule_id: Optional[int] = Query(None, description="排课记录ID"),
    attendance_status: Optional[AttendanceStatusEnum] = Query(None, description="考勤状态"),
    attendance_date_start: Optional[str] = Query(None, description="考勤日期范围-起始"),
    attendance_date_end: Optional[str] = Query(None, description="考勤日期范围-结束")
) -> JSONResponse:
    """考勤记录列表"""
    search = ClassAttendanceQueryParam(
        student_id=student_id,
        class_id=class_id,
        schedule_id=schedule_id,
        attendance_status=attendance_status,
        attendance_date_start=attendance_date_start,
        attendance_date_end=attendance_date_end
    )
    result = await ClassAttendanceService.page_service(auth, page_no, page_size, search)
    return SuccessResponse(data=result, msg="考勤记录列表获取成功")

@BadmintonRouter.get("/class-attendances/{id}", summary="考勤记录详情", description="获取考勤记录详细信息")
async def class_attendance_detail(
    id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class_attendance:detail"]))
) -> JSONResponse:
    """考勤记录详情"""
    result = await ClassAttendanceService.detail_service(auth, id)
    return SuccessResponse(data=result, msg="考勤记录详情获取成功")

@BadmintonRouter.put("/class-attendances/{id}", summary="更新考勤记录", description="更新考勤记录信息")
async def class_attendance_update(
    id: int,
    data: ClassAttendanceUpdateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class_attendance:update"]))
) -> JSONResponse:
    """更新考勤记录"""
    result = await ClassAttendanceService.update_service(auth, id, data)
    return SuccessResponse(data=result, msg="考勤记录更新成功")

@BadmintonRouter.delete("/class-attendances", summary="删除考勤记录", description="批量删除考勤记录")
async def class_attendance_delete(
    ids: str = Query(..., description="考勤记录ID列表，用逗号分隔"),
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class_attendance:delete"]))
) -> JSONResponse:
    """删除考勤记录"""
    id_list = [int(id) for id in ids.split(",")]
    result = await ClassAttendanceService.delete_service(auth, id_list)
    return SuccessResponse(data=result, msg="考勤记录删除成功")

@BadmintonRouter.get("/class-attendances/student/{student_id}", summary="学员考勤记录", description="获取指定学员的所有考勤记录")
async def class_attendances_by_student(
    student_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class_attendance:list"]))
) -> JSONResponse:
    """学员考勤记录"""
    result = await ClassAttendanceService.get_by_student_service(auth, student_id)
    return SuccessResponse(data=result, msg="学员考勤记录获取成功")

@BadmintonRouter.get("/class-attendances/class/{class_id}", summary="班级考勤记录", description="获取指定班级的所有考勤记录")
async def class_attendances_by_class(
    class_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class_attendance:list"]))
) -> JSONResponse:
    """班级考勤记录"""
    result = await ClassAttendanceService.get_by_class_service(auth, class_id)
    return SuccessResponse(data=result, msg="班级考勤记录获取成功")


# ============================================================================
# 学期制课时结算系统 - 排课记录管理 API
# ============================================================================

@BadmintonRouter.post("/class-schedules", summary="创建排课记录", description="创建新排课记录")
async def class_schedule_create(
    data: ClassScheduleCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class_schedule:create"]))
) -> JSONResponse:
    """创建排课记录"""
    result = await ClassScheduleService.create_service(auth, data)
    return SuccessResponse(data=result, msg="排课记录创建成功")

@BadmintonRouter.get("/class-schedules", summary="排课记录列表", description="获取排课记录列表（支持分页和查询）")
async def class_schedule_list(
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class_schedule:list"])),
    page_no: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    class_id: Optional[int] = Query(None, description="班级ID"),
    schedule_date_start: Optional[str] = Query(None, description="排课日期范围-起始"),
    schedule_date_end: Optional[str] = Query(None, description="排课日期范围-结束"),
    schedule_status: Optional[ScheduleStatusEnum] = Query(None, description="排课状态")
) -> JSONResponse:
    """排课记录列表"""
    search = ClassScheduleQueryParam(
        class_id=class_id,
        schedule_date_start=schedule_date_start,
        schedule_date_end=schedule_date_end,
        schedule_status=schedule_status
    )
    result = await ClassScheduleService.page_service(auth, page_no, page_size, search)
    return SuccessResponse(data=result, msg="排课记录列表获取成功")

@BadmintonRouter.get("/class-schedules/{id}", summary="排课记录详情", description="获取排课记录详细信息")
async def class_schedule_detail(
    id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class_schedule:detail"]))
) -> JSONResponse:
    """排课记录详情"""
    result = await ClassScheduleService.detail_service(auth, id)
    return SuccessResponse(data=result, msg="排课记录详情获取成功")

@BadmintonRouter.put("/class-schedules/{id}", summary="更新排课记录", description="更新排课记录信息")
async def class_schedule_update(
    id: int,
    data: ClassScheduleUpdateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class_schedule:update"]))
) -> JSONResponse:
    """更新排课记录"""
    result = await ClassScheduleService.update_service(auth, id, data)
    return SuccessResponse(data=result, msg="排课记录更新成功")

@BadmintonRouter.delete("/class-schedules", summary="删除排课记录", description="批量删除排课记录")
async def class_schedule_delete(
    ids: str = Query(..., description="排课记录ID列表，用逗号分隔"),
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class_schedule:delete"]))
) -> JSONResponse:
    """删除排课记录"""
    id_list = [int(id) for id in ids.split(",")]
    result = await ClassScheduleService.delete_service(auth, id_list)
    return SuccessResponse(data=result, msg="排课记录删除成功")

@BadmintonRouter.get("/class-schedules/class/{class_id}", summary="班级排课记录", description="获取指定班级的所有排课记录")
async def class_schedules_by_class(
    class_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class_schedule:list"]))
) -> JSONResponse:
    """班级排课记录"""
    result = await ClassScheduleService.get_by_class_service(auth, class_id)
    return SuccessResponse(data=result, msg="班级排课记录获取成功")

@BadmintonRouter.get("/class-schedules/class/{class_id}/upcoming", summary="即将上课", description="获取指定班级的即将上课排课记录")
async def class_schedules_upcoming(
    class_id: int,
    days: int = Query(7, ge=1, le=30, description="查询天数"),
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class_schedule:list"]))
) -> JSONResponse:
    """即将上课"""
    result = await ClassScheduleService.get_upcoming_service(auth, class_id, days)
    return SuccessResponse(data=result, msg="即将上课排课记录获取成功")
