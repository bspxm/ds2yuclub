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
from app.core.dependencies import AuthPermission, get_current_user
from app.core.exceptions import CustomException
from app.core.router_class import OperationLogRoute

from ..attendance.service import ClassAttendanceService
from ..tournament.crud import TournamentParticipantCRUD
from .crud import StudentCRUD, ParentStudentCRUD
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


@ParentStudentRouter.get(
    "/list-all",
    summary="关联列表(管理端)",
    description="获取所有家长-学员关联列表",
)
async def parent_student_list_all(
    auth: AuthSchema = Depends(
        AuthPermission(["module_badminton:parent_student:list"])
    ),
) -> JSONResponse:
    """获取所有关联（管理端）"""
    relations = await ParentStudentCRUD(auth).list_crud(
        order_by=[{"id": "desc"}],
        preload=["parent", "student"],
    )
    result = []
    for rel in relations:
        result.append({
            "id": rel.id,
            "parent_id": rel.parent_id,
            "student_id": rel.student_id,
            "relation_type": rel.relation_type.value if rel.relation_type else None,
            "is_primary": rel.is_primary,
            "parent_name": rel.parent.name if rel.parent else "",
            "student_name": rel.student.name if rel.student else "",
        })
    return SuccessResponse(data=result, msg="获取成功")


# ============================================================================
# 家长移动端 API（家长角色专用，基于 role.code = PARENTS 认证）
# ============================================================================


async def require_parent_role(auth: AuthSchema = Depends(get_current_user)) -> AuthSchema:
    if auth.user and auth.user.is_superuser:
        return auth
    if auth.user and auth.user.roles:
        for role in auth.user.roles:
            if role.code == "PARENTS" and role.status == "0":
                return auth
    raise CustomException(msg="无权限操作", code=10403, status_code=403)


@ParentStudentRouter.get(
    "/my-students",
    summary="我的学员(家长移动端)",
    description="获取当前登录家长关联的所有学员",
)
async def parent_my_students(
    auth: AuthSchema = Depends(require_parent_role),
) -> JSONResponse:
    """获取当前家长的学员（家长移动端使用）"""
    parent_id = auth.user.id
    result = await ParentStudentService.get_by_parent_service(auth, parent_id)
    return SuccessResponse(data=result, msg="获取成功")


@ParentStudentRouter.get(
    "/my-students/{student_id}/attendances",
    summary="我的学员考勤(家长移动端)",
    description="获取家长关联学员的考勤记录",
)
async def parent_my_student_attendances(
    student_id: int,
    auth: AuthSchema = Depends(require_parent_role),
) -> JSONResponse:
    """获取家长关联学员的考勤记录"""
    parent_id = auth.user.id
    relations = await ParentStudentService.get_by_parent_service(auth, parent_id)
    child_ids = [r["student"]["id"] for r in relations]
    if student_id not in child_ids:
        raise CustomException(msg="无权限查看该学员数据", code=10403, status_code=403)

    result = await ClassAttendanceService.get_by_student_service(auth, student_id)
    return SuccessResponse(data=result, msg="获取成功")


@ParentStudentRouter.get(
    "/my-students/{student_id}/tournaments",
    summary="我的学员赛事(家长移动端)",
    description="获取家长关联学员的赛事报名记录",
)
async def parent_my_student_tournaments(
    student_id: int,
    auth: AuthSchema = Depends(require_parent_role),
) -> JSONResponse:
    """获取家长关联学员的赛事报名记录"""
    parent_id = auth.user.id
    relations = await ParentStudentService.get_by_parent_service(auth, parent_id)
    child_ids = [r["student"]["id"] for r in relations]
    if student_id not in child_ids:
        raise CustomException(msg="无权限查看该学员数据", code=10403, status_code=403)

    from sqlalchemy import text as sa_text

    participants = await TournamentParticipantCRUD(auth).list(
        search={"student_id": student_id},
        preload=["tournament"],
        order_by=[{"id": "desc"}],
    )
    result = []
    for p in participants:
        tournament = p.tournament
        pid = p.id

        row = (
            await auth.db.execute(
                sa_text(
                    "SELECT "
                    "  COUNT(*) FILTER (WHERE status = 'COMPLETED') AS matches_played, "
                    "  COUNT(*) FILTER (WHERE status = 'COMPLETED' AND winner_id = :pid) AS matches_won, "
                    "  COUNT(*) FILTER (WHERE status = 'COMPLETED' AND winner_id IS NOT NULL AND winner_id != :pid2) AS matches_lost "
                    "FROM badminton_tournament_match "
                    "WHERE tournament_id = :tid AND (player1_id = :pid3 OR player2_id = :pid4)"
                ),
                {"pid": pid, "pid2": pid, "pid3": pid, "pid4": pid, "tid": p.tournament_id},
            )
        ).one()

        played = row.matches_played or 0
        won = row.matches_won or 0
        lost = row.matches_lost or 0

        result.append({
            "id": p.id,
            "tournament_id": p.tournament_id,
            "student_id": p.student_id,
            "is_withdrawn": p.is_withdrawn,
            "final_rank": p.final_rank,
            "matches_played": played,
            "matches_won": won,
            "matches_lost": lost,
            "tournament_name": tournament.name if tournament else "",
            "tournament_type": tournament.tournament_type.value if tournament and tournament.tournament_type else "",
            "tournament_status": tournament.status.value if tournament and tournament.status else "",
            "start_date": tournament.start_date.isoformat() if tournament and tournament.start_date else "",
            "end_date": tournament.end_date.isoformat() if tournament and tournament.end_date else "",
            "description": tournament.description if tournament else "",
        })
    return SuccessResponse(data=result, msg="获取成功")


@ParentStudentRouter.get(
    "/my-students/{student_id}/assessments/latest",
    summary="我的学员最新评估(家长移动端)",
    description="获取家长关联学员的最新能力评估",
)
async def parent_my_student_assessment_latest(
    student_id: int,
    auth: AuthSchema = Depends(require_parent_role),
) -> JSONResponse:
    """获取家长关联学员的最新评估"""
    parent_id = auth.user.id
    relations = await ParentStudentService.get_by_parent_service(auth, parent_id)
    child_ids = [r["student"]["id"] for r in relations]
    if student_id not in child_ids:
        raise CustomException(msg="无权限查看该学员数据", code=10403, status_code=403)

    result = await AbilityAssessmentService.get_latest_service(auth, student_id)
    if not result:
        return SuccessResponse(data=None, msg="该学员暂无评估记录")
    return SuccessResponse(data=result, msg="最新评估获取成功")


@ParentStudentRouter.get(
    "/my-students/{student_id}/assessments/history",
    summary="我的学员评估历史(家长移动端)",
    description="获取家长关联学员的能力评估历史",
)
async def parent_my_student_assessment_history(
    student_id: int,
    auth: AuthSchema = Depends(require_parent_role),
    limit: int = Query(5, ge=1, le=20, description="返回记录数"),
) -> JSONResponse:
    parent_id = auth.user.id
    relations = await ParentStudentService.get_by_parent_service(auth, parent_id)
    child_ids = [r["student"]["id"] for r in relations]
    if student_id not in child_ids:
        raise CustomException(msg="无权限查看该学员数据", code=10403, status_code=403)

    result = await AbilityAssessmentService.get_history_service(auth, student_id, limit)
    return SuccessResponse(data=result, msg="获取成功")


@ParentStudentRouter.get(
    "/match-by-mobile",
    summary="手机号匹配学员(家长端)",
    description="根据当前家长手机号查找匹配且未绑定的学员",
)
async def parent_match_by_mobile(
    auth: AuthSchema = Depends(require_parent_role),
) -> JSONResponse:
    mobile = auth.user.mobile
    if not mobile:
        return SuccessResponse(data=[], msg="当前账号未设置手机号")

    students = await StudentCRUD(auth).list_crud(
        search={"mobile": ("eq", mobile)},
    )
    existing = await ParentStudentCRUD(auth).get_by_parent_id_crud(auth.user.id)
    existing_ids = {r.student_id for r in existing}

    result = []
    for s in students:
        if s.id not in existing_ids:
            result.append({
                "id": s.id,
                "name": s.name,
                "mobile": s.mobile,
                "level": s.level,
                "group_name": s.group_name,
            })
    return SuccessResponse(data=result, msg="获取成功")


@ParentStudentRouter.post(
    "/self-bind",
    summary="自助绑定学员(家长端)",
    description="家长自助绑定手机号匹配的学员",
)
async def parent_self_bind(
    data: dict,
    auth: AuthSchema = Depends(require_parent_role),
) -> JSONResponse:
    student_id = data.get("student_id")
    if not student_id:
        raise CustomException(msg="请提供学员ID")

    mobile = auth.user.mobile
    if not mobile:
        raise CustomException(msg="当前账号未设置手机号")

    students = await StudentCRUD(auth).list_crud(
        search={"id": ("eq", student_id), "mobile": ("eq", mobile)},
    )
    if not students:
        raise CustomException(msg="该学员与您的手机号不匹配")

    existing = await ParentStudentCRUD(auth).get(
        parent_id=auth.user.id,
        student_id=student_id,
    )
    if existing:
        raise CustomException(msg="该学员已绑定")

    from .schema import ParentStudentCreateSchema

    create_data = ParentStudentCreateSchema(
        parent_id=auth.user.id,
        student_id=student_id,
        relation_type="other",
        is_primary=True,
    )
    relation = await ParentStudentService.create_service(auth, create_data)
    return SuccessResponse(data=relation, msg="绑定成功")
