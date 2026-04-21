"""
tournament模块 - 控制器
"""

from typing import Optional
from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import JSONResponse

from app.api.v1.module_system.auth.schema import AuthSchema
from app.common.response import SuccessResponse
from app.core.dependencies import AuthPermission
from app.core.exceptions import CustomException
from app.core.router_class import OperationLogRoute

# 淘汰赛相关导入
from .knockout_service import KnockoutService
from .schema import (
    TournamentCreateSchema,
    TournamentUpdateSchema,
    MatchScoreSchema,
    BatchAddParticipantsSchema,
    ChallengeCreateSchema,
)
from .service import (
    TournamentService,
    TournamentParticipantService,
    TournamentMatchService,
)
from ..enums import TournamentTypeEnum

TournamentRouter = APIRouter(
    route_class=OperationLogRoute, prefix="/tournament", tags=["tournament管理"]
)


@TournamentRouter.post("", summary="创建赛事", description="创建新赛事")
async def tournament_create(
    data: TournamentCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:create"])),
) -> JSONResponse:
    """创建赛事"""
    result = await TournamentService.create_service(auth, data)
    return SuccessResponse(data=result, msg="赛事创建成功")


@TournamentRouter.get("", summary="赛事列表", description="获取赛事列表")
async def tournament_list(
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:list"])),
) -> JSONResponse:
    """赛事列表"""
    result = await TournamentService.list_service(auth)
    return SuccessResponse(data=result, msg="赛事列表获取成功")


@TournamentRouter.get("/active", summary="进行中赛事", description="获取进行中的赛事")
async def tournament_active(
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:list"])),
) -> JSONResponse:
    """进行中赛事"""
    result = await TournamentService.get_active_service(auth)
    return SuccessResponse(data=result, msg="进行中赛事获取成功")


@TournamentRouter.put(
    "/{tournament_id}",
    summary="更新赛事",
    description="更新赛事信息",
)
async def tournament_update(
    tournament_id: int,
    data: TournamentUpdateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:update"])),
) -> JSONResponse:
    """更新赛事"""
    result = await TournamentService.update_service(auth, tournament_id, data)
    return SuccessResponse(data=result, msg="赛事更新成功")


@TournamentRouter.delete("", summary="删除赛事", description="批量删除赛事")
async def tournament_delete(
    data: list[int],
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:delete"])),
) -> JSONResponse:
    """删除赛事"""
    await TournamentService.delete_service(auth, data)
    return SuccessResponse(msg="赛事删除成功")


@TournamentRouter.post(
    "/{tournament_id}/participants/batch",
    summary="批量添加参赛队员",
    description="为赛事批量添加参赛队员",
)
async def batch_add_participants(
    tournament_id: int,
    data: BatchAddParticipantsSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:create"])),
) -> JSONResponse:
    result = await TournamentParticipantService.batch_add_service(
        tournament_id, data.student_ids, auth
    )
    return SuccessResponse(data=result, msg="参赛队员添加成功")


@TournamentRouter.get(
    "/{tournament_id}/participants",
    summary="获取参赛队员列表",
    description="获取指定赛事的参赛队员列表",
)
async def get_participants(
    tournament_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:list"])),
) -> JSONResponse:
    result = await TournamentParticipantService.get_by_tournament_service(
        tournament_id, auth
    )
    return SuccessResponse(data=result, msg="参赛队员获取成功")


@TournamentRouter.delete(
    "/{tournament_id}/participants/{participant_id}",
    summary="移除参赛队员",
    description="从赛事中移除参赛队员",
)
async def remove_participant(
    tournament_id: int,
    participant_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:delete"])),
) -> JSONResponse:
    await TournamentParticipantService.remove_service(
        tournament_id, participant_id, auth
    )
    return SuccessResponse(msg="参赛队员移除成功")


@TournamentRouter.put(
    "/{tournament_id}/participants/{participant_id}",
    summary="更新参赛队员",
    description="更新参赛队员信息（种子排名等）",
)
async def update_participant(
    tournament_id: int,
    participant_id: int,
    seed_rank: Optional[int] = None,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:update"])),
) -> JSONResponse:
    result = await TournamentParticipantService.update_service(
        tournament_id, participant_id, seed_rank, auth
    )
    return SuccessResponse(data=result, msg="参赛队员更新成功")


@TournamentRouter.post(
    "/{tournament_id}/generate-matches",
    summary="生成对阵表",
    description="根据赛事类型生成比赛对阵表",
)
async def generate_matches(
    tournament_id: int,
    use_seeding: bool = Query(True, description="是否使用种子排名"),
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:create"])),
) -> JSONResponse:
    result = await TournamentMatchService.generate_matches_service(
        tournament_id, use_seeding, auth
    )
    return SuccessResponse(data=result, msg="对阵表生成成功")


@TournamentRouter.get(
    "/{tournament_id}/matches",
    summary="获取对阵列表",
    description="获取赛事的比赛对阵列表",
)
async def get_matches(
    tournament_id: int,
    group_id: Optional[int] = Query(None, description="分组ID筛选"),
    round_type: Optional[str] = Query(None, description="轮次类型筛选"),
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:list"])),
) -> JSONResponse:
    result = await TournamentMatchService.get_matches_service(
        tournament_id, group_id, round_type, auth
    )
    return SuccessResponse(data=result, msg="对阵列表获取成功")


@TournamentRouter.get(
    "/{tournament_id}/group-stage-data",
    summary="获取小组赛数据",
    description="获取羽球在线风格的小组赛数据（对阵矩阵、积分排名、赛程）",
)
async def get_group_stage_data(
    tournament_id: int,
    group_id: Optional[int] = Query(None, description="分组ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:list"])),
) -> JSONResponse:
    result = await TournamentMatchService.get_group_stage_data_service(
        tournament_id, group_id, auth
    )
    return SuccessResponse(data=result, msg="小组赛数据获取成功")


@TournamentRouter.get(
    "/{tournament_id}/matches/{match_id}",
    summary="获取比赛详情",
    description="获取单场比赛的详细信息",
)
async def get_match_detail(
    tournament_id: int,
    match_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:list"])),
) -> JSONResponse:
    result = await TournamentMatchService.get_match_detail_service(
        tournament_id, match_id, auth
    )
    return SuccessResponse(data=result, msg="比赛详情获取成功")


@TournamentRouter.put(
    "/{tournament_id}/matches/{match_id}/score",
    summary="录入比分",
    description="为比赛录入比分",
)
async def record_score(
    tournament_id: int,
    match_id: int,
    scores: MatchScoreSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:update"])),
) -> JSONResponse:
    result = await TournamentMatchService.record_score_service(
        tournament_id, match_id, scores, auth
    )
    return SuccessResponse(data=result, msg="比分录入成功")


@TournamentRouter.get(
    "/{tournament_id}/rankings", summary="获取排名", description="获取赛事排名"
)
async def get_rankings(
    tournament_id: int,
    group_id: Optional[int] = Query(None, description="分组ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:list"])),
) -> JSONResponse:
    result = await TournamentService.get_rankings_service(tournament_id, group_id, auth)
    return SuccessResponse(data=result, msg="排名获取成功")


@TournamentRouter.get(
    "/h2h", summary="H2H查询", description="查询两学员之间的历史对战记录"
)
async def get_h2h(
    student_id_1: int = Query(..., description="学员1ID"),
    student_id_2: int = Query(..., description="学员2ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:list"])),
) -> JSONResponse:
    result = await TournamentService.get_h2h_service(student_id_1, student_id_2, auth)
    return SuccessResponse(data=result, msg="H2H记录获取成功")


@TournamentRouter.get(
    "/{tournament_id}/knockout",
    summary="获取淘汰赛数据",
    description="获取单败淘汰赛的对阵树数据",
)
async def get_knockout(
    tournament_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:list"])),
) -> JSONResponse:
    """获取淘汰赛数据"""
    from .knockout_service import KnockoutService

    result = await KnockoutService.get_knockout_data(tournament_id, auth)
    return SuccessResponse(data=result, msg="淘汰赛数据获取成功")


@TournamentRouter.post(
    "/{tournament_id}/knockout/generate",
    summary="生成淘汰赛对阵表",
    description="根据参赛者生成单败淘汰赛对阵表",
)
async def generate_knockout(
    tournament_id: int,
    participant_ids: list[int],
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:update"])),
) -> JSONResponse:
    """生成淘汰赛对阵表"""
    from .knockout_service import KnockoutService

    result = await KnockoutService.generate_bracket(
        tournament_id, participant_ids, auth
    )
    return SuccessResponse(data=result, msg="淘汰赛对阵表生成成功")


@TournamentRouter.put(
    "/{tournament_id}/knockout/matches/{match_id}/score",
    summary="录入淘汰赛比分",
    description="录入单败淘汰赛比分并自动晋级",
)
async def record_knockout_score(
    tournament_id: int,
    match_id: int,
    scores: MatchScoreSchema,
    winner_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:update"])),
) -> JSONResponse:
    """录入淘汰赛比分"""
    from .knockout_service import KnockoutService

    result = await KnockoutService.update_match(
        match_id, scores.model_dump(), winner_id, auth
    )
    return SuccessResponse(data=result, msg="比分录入成功")


@TournamentRouter.post(
    "/{tournament_id}/championship/generate-knockout",
    summary="生成锦标赛淘汰赛",
    description="小组赛结束后，根据排名生成交叉淘汰赛对阵",
)
async def generate_championship_knockout(
    tournament_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:update"])),
) -> JSONResponse:
    """生成锦标赛淘汰赛对阵"""
    result = await TournamentMatchService._generate_championship_knockout(
        tournament_id, auth
    )
    return SuccessResponse(data=result, msg="锦标赛淘汰赛对阵生成成功")


@TournamentRouter.get(
    "/{tournament_id}/championship/status",
    summary="获取锦标赛状态",
    description="获取锦标赛两阶段（小组赛/淘汰赛）状态概览",
)
async def get_championship_status(
    tournament_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:list"])),
) -> JSONResponse:
    """获取锦标赛状态"""
    result = await TournamentMatchService.get_championship_status(tournament_id, auth)
    return SuccessResponse(data=result, msg="锦标赛状态获取成功")


@TournamentRouter.get(
    "/types",
    summary="获取支持的赛制类型",
    description="获取系统支持的比赛赛制类型",
)
async def get_tournament_types() -> JSONResponse:
    """获取赛制类型"""
    types = [
        {
            "value": TournamentTypeEnum.CHAMPIONSHIP.value,
            "label": "锦标赛",
            "description": "分组循环赛 + 交叉淘汰赛，先小组循环后淘汰争夺冠军",
        },
        {
            "value": TournamentTypeEnum.PURE_GROUP.value,
            "label": "纯小组赛",
            "description": "仅小组循环赛决定名次，适合快速排位",
        },
        {
            "value": TournamentTypeEnum.PROMOTION_RELEGATION.value,
            "label": "定区升降赛",
            "description": "位置挑战赛，趣味性强，位置实时变动",
        },
        {
            "value": TournamentTypeEnum.SINGLE_ELIMINATION.value,
            "label": "单败制淘汰赛",
            "description": "单败淘汰赛，决出所有名次",
        },
    ]
    return SuccessResponse(data=types, msg="赛制类型获取成功")


# ============================================================================
# 定区升降赛（抢位赛）相关路由
# ============================================================================


@TournamentRouter.post(
    "/{tournament_id}/positions/init",
    summary="初始化抢位赛位置",
    description="随机抽签为所有参赛者分配初始位置",
)
async def init_positions(
    tournament_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:create"])),
) -> JSONResponse:
    """初始化抢位赛位置"""
    result = await TournamentMatchService._init_promotion_relegation_positions(
        tournament_id, auth
    )
    return SuccessResponse(data=result, msg="位置初始化成功")


@TournamentRouter.get(
    "/{tournament_id}/positions",
    summary="获取抢位赛位置板",
    description="获取所有参赛者的当前位置",
)
async def get_positions(
    tournament_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:list"])),
) -> JSONResponse:
    """获取位置板"""
    from .crud import TournamentParticipantCRUD

    result = await TournamentParticipantCRUD(auth).get_by_tournament_with_position_crud(
        tournament_id
    )
    return SuccessResponse(data=result, msg="位置板获取成功")


@TournamentRouter.post(
    "/{tournament_id}/rounds/generate",
    summary="生成新一轮",
    description="按当前位置配对生成新一轮比赛，(1,2), (3,4)...",
)
async def generate_round(
    tournament_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:update"])),
) -> JSONResponse:
    """生成新一轮"""
    result = await TournamentMatchService.generate_round_service(tournament_id, auth)
    return SuccessResponse(data=result, msg="新一轮生成成功")


@TournamentRouter.get(
    "/{tournament_id}/pr-matches",
    summary="获取抢位赛比赛记录",
    description="获取定区升降赛的所有比赛记录",
)
async def get_pr_matches(
    tournament_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:tournament:list"])),
) -> JSONResponse:
    """获取抢位赛比赛记录"""
    result = await TournamentMatchService.get_pr_matches_service(tournament_id, auth)
    return SuccessResponse(data=result, msg="比赛记录获取成功")
