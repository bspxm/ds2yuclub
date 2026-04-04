"""
tournament模块 - Service服务层
"""

from datetime import date, datetime, timedelta
from typing import Optional, List, Dict, Any

from sqlalchemy.orm import Session

from app.api.v1.module_system.user.service import UserService
from app.core.base_crud import BaseCRUD
from app.core.database import SessionDep
from app.core.exceptions import CustomException
from app.core.logger import logger

from .model import *
from .crud import TournamentCRUD, TournamentParticipantCRUD, TournamentMatchCRUD
from .schema import *
from ..enums import TournamentStatusEnum

from app.api.v1.module_system.auth.schema import AuthSchema

# ============================================================================
# 赛事管理服务
# ============================================================================


class TournamentService:
    """赛事管理服务层"""

    @classmethod
    async def create_service(
        cls, auth: AuthSchema, data: TournamentCreateSchema
    ) -> dict:
        """创建赛事"""
        tournament = await TournamentCRUD(auth).create_crud(data=data)
        return TournamentOutSchema.model_validate(tournament).model_dump()

    @classmethod
    async def update_service(
        cls, auth: AuthSchema, tournament_id: int, data: TournamentUpdateSchema
    ) -> dict:
        """更新赛事"""
        logger.info(f"[update_service] 开始更新赛事，tournament_id={tournament_id}")
        tournament = await TournamentCRUD(auth).get_by_id_crud(tournament_id)
        if not tournament:
            logger.error(f"[update_service] 赛事不存在，tournament_id={tournament_id}")
            raise CustomException(msg="赛事不存在")

        # 如果赛事已开始，不能修改某些字段
        if tournament.status != TournamentStatusEnum.DRAFT:
            raise CustomException(msg="赛事已开始，不能修改")

        updated = await TournamentCRUD(auth).update_crud(tournament_id, data=data)
        return TournamentOutSchema.model_validate(updated).model_dump()

    @classmethod
    async def update_status_service(
        cls, auth: AuthSchema, tournament_id: int, status: str
    ) -> dict:
        """更新赛事状态"""
        tournament = await TournamentCRUD(auth).update_status_crud(
            tournament_id, status
        )
        if not tournament:
            raise CustomException(msg="赛事不存在")
        return TournamentOutSchema.model_validate(tournament).model_dump()

    @classmethod
    async def list_service(cls, auth: AuthSchema) -> list[dict]:
        """获取赛事列表（使用视图优化查询性能）"""
        from sqlalchemy import text

        sql = text("""
            SELECT * FROM v_tournament_list 
            ORDER BY created_time DESC
        """)

        result = await auth.db.execute(sql)
        rows = result.mappings().all()

        return [
            {
                "id": row["id"],
                "name": row["name"],
                "tournament_type": row["tournament_type"],
                "status": row["status"],
                "start_date": row["start_date"].isoformat()
                if row["start_date"]
                else None,
                "end_date": row["end_date"].isoformat() if row["end_date"] else None,
                "registration_deadline": row["registration_deadline"].isoformat()
                if row["registration_deadline"]
                else None,
                "max_participants": row["max_participants"],
                "group_size": row["group_size"],
                "num_groups": row["num_groups"],
                "match_format": row["match_format"],
                "points_per_game": row["points_per_game"],
                "description": row["description"],
                "location": row["location"],
                "uuid": row["uuid"],
                "created_time": row["created_time"].isoformat()
                if row["created_time"]
                else None,
                "updated_time": row["updated_time"].isoformat()
                if row["updated_time"]
                else None,
                "created_by": {
                    "id": row["created_by_id"],
                    "name": row["created_by_name"],
                }
                if row["created_by_id"]
                else None,
                "updated_by": {
                    "id": row["updated_by_id"],
                    "name": row["updated_by_name"],
                }
                if row["updated_by_id"]
                else None,
                "participant_count": row["participant_count"],
                "match_count": row["match_count"],
                "completed_match_count": row["completed_match_count"],
            }
            for row in rows
        ]

    @classmethod
    async def get_active_service(cls, auth: AuthSchema) -> list[dict]:
        """获取进行中的赛事"""
        tournaments = await TournamentCRUD(auth).get_active_tournaments_crud()
        return [
            TournamentOutSchema.model_validate(tournament).model_dump()
            for tournament in tournaments
        ]

    @classmethod
    async def delete_service(cls, auth: AuthSchema, ids: list[int]) -> None:
        """删除赛事"""
        for tournament_id in ids:
            tournament = await TournamentCRUD(auth).get_by_id_crud(tournament_id)
            if not tournament:
                raise CustomException(msg="赛事不存在")
            if tournament.status != TournamentStatusEnum.DRAFT:
                raise CustomException(msg="非草稿状态的赛事不能删除")
        await TournamentCRUD(auth).delete_crud(ids)

    @classmethod
    async def get_rankings_service(
        cls, tournament_id: int, group_id: Optional[int], auth: AuthSchema
    ) -> list[dict]:
        """获取赛事排名"""
        tournament = await TournamentCRUD(auth).get_by_id_crud(
            tournament_id, preload=["participants", "matches"]
        )
        if not tournament:
            raise CustomException(msg="赛事不存在")

        from .engine.base import Participant, Match, calculate_ranking_score
        from collections import defaultdict

        participants = tournament.participants
        matches = tournament.matches

        if group_id:
            participants = [p for p in participants if p.group_id == group_id]
            matches = [m for m in matches if m.group_id == group_id]

        participant_stats = {}
        for p in participants:
            p_matches = [
                m for m in matches if m.player1_id == p.id or m.player2_id == p.id
            ]
            stats = {
                "id": p.id,
                "student_id": p.student_id,
                "student_name": p.student.name if p.student else "",
                "seed_rank": p.seed_rank,
                "matches_played": len(p_matches),
                "wins": sum(1 for m in p_matches if m.winner_id == p.id),
                "losses": sum(
                    1
                    for m in p_matches
                    if m.winner_id
                    and m.winner_id != p.id
                    and (m.player1_id == p.id or m.player2_id == p.id)
                ),
            }
            participant_stats[p.id] = stats

        rankings = sorted(
            participant_stats.values(),
            key=lambda x: (
                -x["wins"],
                -(x["wins"] * 21 - (x["matches_played"] - x["wins"]) * 21),
            ),
        )

        for i, r in enumerate(rankings):
            r["rank"] = i + 1

        return rankings

    @classmethod
    async def get_h2h_service(
        cls, student_id_1: int, student_id_2: int, auth: AuthSchema
    ) -> dict:
        """获取两学员之间的H2H记录"""
        from sqlalchemy import select, or_, and_

        stmt = (
            select(TournamentMatchModel)
            .where(
                or_(
                    and_(
                        TournamentMatchModel.player1_id == student_id_1,
                        TournamentMatchModel.player2_id == student_id_2,
                    ),
                    and_(
                        TournamentMatchModel.player1_id == student_id_2,
                        TournamentMatchModel.player2_id == student_id_1,
                    ),
                ),
                TournamentMatchModel.winner_id.isnot(None),
            )
            .order_by(TournamentMatchModel.actual_start_time.desc())
        )

        result = await auth.db.execute(stmt)
        matches = result.scalars().all()

        records = []
        for m in matches:
            records.append(
                {
                    "match_id": m.id,
                    "tournament_id": m.tournament_id,
                    "player1_id": m.player1_id,
                    "player2_id": m.player2_id,
                    "scores": m.scores,
                    "winner_id": m.winner_id,
                    "scheduled_time": m.scheduled_time.isoformat()
                    if m.scheduled_time
                    else None,
                }
            )

        return {
            "student_id_1": student_id_1,
            "student_id_2": student_id_2,
            "total_matches": len(records),
            "student1_wins": sum(1 for r in records if r["winner_id"] == student_id_1),
            "student2_wins": sum(1 for r in records if r["winner_id"] == student_id_2),
            "records": records,
        }


class TournamentParticipantService:
    """参赛队员服务层"""

    @classmethod
    async def batch_add_service(
        cls, tournament_id: int, student_ids: list[int], auth: AuthSchema
    ) -> list[dict]:
        """批量添加参赛队员 - 使用直接SQL查询避免关联加载"""
        from sqlalchemy import select, text
        from app.plugin.module_badminton.tournament.model import TournamentModel

        # 使用直接SQL查询，不加载关联
        result = await auth.db.execute(
            select(TournamentModel.id, TournamentModel.status).where(
                TournamentModel.id == tournament_id
            )
        )
        tournament = result.first()

        if not tournament:
            raise CustomException(msg="赛事不存在")

        if tournament.status != TournamentStatusEnum.DRAFT:
            raise CustomException(msg="赛事已开始，不能添加参赛队员")

        results = []
        for student_id in student_ids:
            try:
                participant = await TournamentParticipantCRUD(auth).register_crud(
                    tournament_id, student_id
                )
                results.append({"student_id": student_id, "status": "added"})
            except ValueError:
                results.append({"student_id": student_id, "status": "already_exists"})

        return results

    @classmethod
    async def get_by_tournament_service(
        cls, tournament_id: int, auth: AuthSchema
    ) -> list[dict]:
        """获取赛事参赛队员列表 - 使用统计视图优化"""
        participants = await TournamentParticipantCRUD(auth).get_by_tournament_crud(
            tournament_id
        )
        # CRUD层已经返回格式化好的数据
        return [
            {
                "id": p["id"],
                "student_id": p["student_id"],
                "student_name": p["student_name"],
                "age": p["age"],
                "group_name": p["group_name"],
                "level": p["level"],
                "seed_rank": p["seed_rank"],
                "final_rank": p["final_rank"],
                "group_id": p["group_id"],
                "matches_played": p["matches_played"],
                "wins": p["matches_won"],
                "losses": p["matches_lost"],
            }
            for p in participants
        ]

    @classmethod
    async def remove_service(
        cls, tournament_id: int, participant_id: int, auth: AuthSchema
    ) -> None:
        """移除参赛队员"""
        tournament = await TournamentCRUD(auth).get_by_id_crud(tournament_id)
        if not tournament:
            raise CustomException(msg="赛事不存在")

        if tournament.status != TournamentStatusEnum.DRAFT:
            raise CustomException(msg="赛事已开始，不能移除参赛队员")

        await TournamentParticipantCRUD(auth).withdraw_crud(participant_id)

    @classmethod
    async def update_service(
        cls,
        tournament_id: int,
        participant_id: int,
        seed_rank: Optional[int],
        auth: AuthSchema,
    ) -> dict:
        """更新参赛队员信息"""
        participant = await TournamentParticipantCRUD(auth).get(id=participant_id)
        if not participant or participant.tournament_id != tournament_id:
            raise CustomException(msg="参赛队员不存在")

        update_data = {}
        if seed_rank is not None:
            update_data["seed_rank"] = seed_rank

        if update_data:
            await TournamentParticipantCRUD(auth).update(participant_id, update_data)

        participant = await TournamentParticipantCRUD(auth).get(id=participant_id)
        return {
            "id": participant.id,
            "student_id": participant.student_id,
            "student_name": participant.student.name if participant.student else "",
            "seed_rank": participant.seed_rank,
        }


class TournamentMatchService:
    """比赛服务层"""

    @classmethod
    async def generate_matches_service(
        cls, tournament_id: int, use_seeding: bool, auth: AuthSchema
    ) -> list[dict]:
        """生成对阵表"""
        logger.info(
            f"[generate_matches_service] 开始生成对阵表，tournament_id={tournament_id}, use_seeding={use_seeding}"
        )
        tournament = await TournamentCRUD(auth).get_by_id_crud(
            tournament_id, preload=["participants"]
        )
        if not tournament:
            raise CustomException(msg="赛事不存在")

        if not tournament.participants:
            raise CustomException(msg="没有参赛队员")

        logger.info(
            f"[generate_matches_service] 赛事名称={tournament.name}, 参赛人数={len(tournament.participants)}"
        )

        from .engine.base import (
            TournamentEngineFactory,
            TournamentType,
            MatchFormat,
            Participant,
            Group,
        )

        tournament_type_map = {
            "round_robin": TournamentType.ROUND_ROBIN,
            "pure_group": TournamentType.PURE_GROUP,
            "promotion_relegation": TournamentType.PROMOTION_RELEGATION,
            "single_elimination": TournamentType.SINGLE_ELIMINATION,
        }

        engine_type = tournament_type_map.get(
            tournament.tournament_type.value, TournamentType.ROUND_ROBIN
        )

        format_map = {
            "best_of_three_21": MatchFormat.BEST_OF_THREE_21,
            "best_of_five_21": MatchFormat.BEST_OF_FIVE_21,
            "one_game_31": MatchFormat.ONE_GAME_31,
            "one_game_15": MatchFormat.ONE_GAME_15,
        }
        match_format = format_map.get(
            tournament.match_format, MatchFormat.BEST_OF_THREE_21
        )

        engine = TournamentEngineFactory.create_engine(
            engine_type,
            match_format=match_format,
            points_per_game=tournament.points_per_game or 21,
            group_size=tournament.group_size,
            num_groups=tournament.num_groups,
            use_seeding=use_seeding,
        )
        logger.info(
            f"[generate_matches_service] 引擎创建成功，engine_type={engine_type}, match_format={match_format}"
        )

        participants = [
            Participant(
                id=p.id,
                name=p.student.name if p.student else f"Player {p.student_id}",
                seed_rank=p.seed_rank,
            )
            for p in tournament.participants
        ]
        logger.info(f"[generate_matches_service] 参赛者数量={len(participants)}")

        groups = engine.create_groups(participants)
        logger.info(f"[generate_matches_service] 分组创建成功，分组数量={len(groups)}")

        matches = engine.generate_matches(groups)
        logger.info(f"[generate_matches_service] 引擎生成对阵数量={len(matches)}")

        match_crud = TournamentMatchCRUD(auth)
        created_matches = []
        for m in matches:
            round_type_value = (
                m.round_type.value if hasattr(m.round_type, "value") else m.round_type
            )
            match_model = await match_crud.create_match_crud(
                tournament_id=tournament_id,
                round_type=round_type_value,
                round_number=m.round_number,
                match_number=m.match_number,
                player1_id=m.player1_id,
                player2_id=m.player2_id,
            )
            if match_model:
                created_matches.append(
                    {
                        "id": match_model.id,
                        "round_number": match_model.round_number,
                        "match_number": match_model.match_number,
                        "player1_id": match_model.player1_id,
                        "player2_id": match_model.player2_id,
                        "round_type": match_model.round_type.value
                        if hasattr(match_model.round_type, "value")
                        else match_model.round_type,
                        "status": match_model.status.value
                        if hasattr(match_model.status, "value")
                        else match_model.status,
                    }
                )
            else:
                logger.error(
                    f"[generate_matches_service] 数据库对阵创建失败: round={m.round_number}, match={m.match_number}"
                )

        logger.info(
            f"[generate_matches_service] 总共创建了{len(created_matches)}个数据库对阵记录"
        )
        return created_matches

    @classmethod
    async def get_matches_service(
        cls,
        tournament_id: int,
        group_id: Optional[int],
        round_type: Optional[str],
        auth: AuthSchema,
    ) -> list[dict]:
        """获取对阵列表（使用视图优化查询性能）"""
        from sqlalchemy import text

        logger.info(
            f"[get_matches_service] 开始查询对阵，tournament_id={tournament_id}, group_id={group_id}, round_type={round_type}"
        )

        # 使用视图查询，避免关联查询
        sql = text("""
            SELECT * FROM v_tournament_match 
            WHERE tournament_id = :tournament_id
            ORDER BY round_number, match_number
        """)

        params = {"tournament_id": tournament_id}
        result = await auth.db.execute(sql, params)
        rows = result.mappings().all()

        logger.info(f"[get_matches_service] 查询到{len(rows)}个对阵记录")

        # 过滤 group_id 和 round_type
        matches = []
        for row in rows:
            if group_id and row["group_id"] != group_id:
                continue
            if round_type and row["round_type"] != round_type:
                continue

            player1_name = row["player1_name"] or f"Player {row['player1_id']}"
            player2_name = row["player2_name"] or f"Player {row['player2_id']}"

            match_data = {
                "id": row["id"],
                "round_number": row["round_number"],
                "match_number": row["match_number"],
                "round_type": row["round_type"],
                "status": row["status"],
                "player1": {
                    "id": row["player1_id"],
                    "student_id": row["player1_student_id"],
                    "name": player1_name,
                    "student_name": player1_name,
                }
                if row["player1_id"]
                else None,
                "player2": {
                    "id": row["player2_id"],
                    "student_id": row["player2_student_id"],
                    "name": player2_name,
                    "student_name": player2_name,
                }
                if row["player2_id"]
                else None,
                "scores": (
                    row["scores"].get("sets", [])
                    if isinstance(row["scores"], dict)
                    else []
                ),
                "winner_id": row["winner_id"],
            }
            matches.append(match_data)

        logger.info(f"[get_matches_service] 返回{len(matches)}个对阵数据")
        return matches

    @classmethod
    async def get_match_detail_service(
        cls, tournament_id: int, match_id: int, auth: AuthSchema
    ) -> dict:
        """获取比赛详情"""
        m = await TournamentMatchCRUD(auth).get(id=match_id)
        if not m or m.tournament_id != tournament_id:
            raise CustomException(msg="比赛不存在")

        return {
            "id": m.id,
            "tournament_id": m.tournament_id,
            "round_number": m.round_number,
            "match_number": m.match_number,
            "round_type": m.round_type.value
            if hasattr(m.round_type, "value")
            else m.round_type,
            "status": m.status.value if hasattr(m.status, "value") else m.status,
            "player1_id": m.player1_id,
            "player2_id": m.player2_id,
            "scores": m.scores,
            "winner_id": m.winner_id,
            "scheduled_time": m.scheduled_time.isoformat()
            if m.scheduled_time
            else None,
        }

    @classmethod
    async def record_score_service(
        cls,
        tournament_id: int,
        match_id: int,
        scores: MatchScoreSchema,
        auth: AuthSchema,
    ) -> dict:
        """录入比分 - 允许添加任意多局，每局独立计分"""
        import time
        from sqlalchemy import select
        from app.plugin.module_badminton.tournament.model import TournamentMatchModel

        start_time = time.time()

        logger.info(f"[record_score_service] 开始录入比分，match_id={match_id}")

        step1_start = time.time()
        # 使用直接SQL查询，避免关联加载
        result = await auth.db.execute(
            select(
                TournamentMatchModel.id,
                TournamentMatchModel.tournament_id,
                TournamentMatchModel.player1_id,
                TournamentMatchModel.player2_id,
            ).where(TournamentMatchModel.id == match_id)
        )
        m = result.first()
        step1_time = time.time() - step1_start
        logger.info(f"[record_score_service] 步骤1-查询比赛: {step1_time:.3f}s")

        if not m or m.tournament_id != tournament_id:
            raise CustomException(msg="比赛不存在")

        # 存储比分数据，包含每局的胜负标记
        sets_data = []
        for s in scores.sets:
            set_data = {
                "player1": s.player1,
                "player2": s.player2,
                "winner": None,  # 每局胜者：1=player1, 2=player2, None=平局
            }
            if s.player1 > s.player2:
                set_data["winner"] = 1
            elif s.player2 > s.player1:
                set_data["winner"] = 2
            sets_data.append(set_data)

        scores_data = {"sets": sets_data}
        step2_time = time.time() - start_time
        logger.info(f"[record_score_service] 步骤2-准备数据: {step2_time:.3f}s")

        # 计算总局数胜负
        p1_wins = sum(1 for s in sets_data if s["winner"] == 1)
        p2_wins = sum(1 for s in sets_data if s["winner"] == 2)

        # 比赛始终处于进行中状态，不自动结束
        # 只有一方领先且总局数>=2时才标记胜者（但仍可继续添加局数）
        winner_id = None
        if p1_wins > p2_wins and (p1_wins >= 2 or p2_wins == 0):
            winner_id = m.player1_id
        elif p2_wins > p1_wins and (p2_wins >= 2 or p1_wins == 0):
            winner_id = m.player2_id

        step3_start = time.time()
        # 使用优化的更新方法
        result = await TournamentMatchCRUD(auth).update_score_crud(
            match_id=match_id,
            scores=scores_data,
            winner_id=winner_id,
            status="IN_PROGRESS",  # 始终为进行中，允许继续添加局数
        )
        step3_time = time.time() - step3_start
        logger.info(f"[record_score_service] 步骤3-更新数据库: {step3_time:.3f}s")

        if not result:
            raise CustomException(msg="更新比分失败")

        total_time = time.time() - start_time
        logger.info(f"[record_score_service] 总计耗时: {total_time:.3f}s")

        return result

    @classmethod
    async def get_group_stage_data_service(
        cls,
        tournament_id: int,
        group_id: Optional[int],
        auth: AuthSchema,
    ) -> dict:
        """获取羽球在线风格的小组赛数据"""
        from sqlalchemy import text

        # 1. 获取分组内的所有选手
        participants_sql = text("""
            SELECT 
                p.id,
                p.student_id,
                s.name as student_name,
                p.seed_rank
            FROM badminton_tournament_participant p
            JOIN badminton_student s ON p.student_id = s.id
            WHERE p.tournament_id = :tournament_id
            AND p.is_withdrawn = false
            ORDER BY p.seed_rank NULLS LAST, p.id
        """)

        result = await auth.db.execute(
            participants_sql, {"tournament_id": tournament_id}
        )
        participants = result.mappings().all()

        if not participants:
            return {"matrix": [], "rankings": [], "schedule": []}

        participant_ids = [p["id"] for p in participants]
        participant_map = {p["id"]: p for p in participants}

        # 2. 获取所有已完成的比赛
        matches_sql = text("""
            SELECT 
                m.id,
                m.player1_id,
                m.player2_id,
                m.scores,
                m.winner_id,
                m.scheduled_time
            FROM badminton_tournament_match m
            WHERE m.tournament_id = :tournament_id
            AND m.round_type = 'GROUP_STAGE'
            AND m.player1_id = ANY(:participant_ids)
            AND m.player2_id = ANY(:participant_ids)
            ORDER BY m.scheduled_time
        """)

        result = await auth.db.execute(
            matches_sql,
            {"tournament_id": tournament_id, "participant_ids": participant_ids},
        )
        matches = result.mappings().all()

        # 3. 构建对阵矩阵
        matrix = []
        for p1 in participants:
            row = {
                "participant_id": p1["id"],
                "student_name": p1["student_name"],
                "results": [],
            }
            for p2 in participants:
                if p1["id"] == p2["id"]:
                    row["results"].append(None)  # 对角线
                else:
                    # 查找两人之间的比赛
                    match = None
                    for m in matches:
                        if (
                            m["player1_id"] == p1["id"] and m["player2_id"] == p2["id"]
                        ) or (
                            m["player1_id"] == p2["id"] and m["player2_id"] == p1["id"]
                        ):
                            match = m
                            break

                    if match and match["scores"]:
                        scores = match["scores"]
                        if isinstance(scores, dict) and "sets" in scores:
                            # 计算总局数
                            p1_sets = 0
                            p2_sets = 0
                            # 构建每局详细比分字符串
                            set_scores = []
                            for s in scores["sets"]:
                                p1_score = s.get("player1", 0)
                                p2_score = s.get("player2", 0)
                                set_scores.append(f"{p1_score}:{p2_score}")
                                if p1_score > p2_score:
                                    p1_sets += 1
                                elif p2_score > p1_score:
                                    p2_sets += 1

                            # 确定方向和胜负平
                            is_draw = p1_sets == p2_sets
                            # 根据方向调整比分显示
                            if match["player1_id"] == p1["id"]:
                                # p1是player1，显示原始比分
                                detail_score = ", ".join(set_scores)
                                row["results"].append(
                                    {
                                        "win": p1_sets > p2_sets and not is_draw,
                                        "draw": is_draw,
                                        "score": f"{p1_sets}:{p2_sets}",
                                        "detail_score": detail_score,
                                        "sets": scores["sets"],
                                    }
                                )
                            else:
                                # p1是player2，需要反转每局比分显示
                                reversed_scores = []
                                for s in scores["sets"]:
                                    p1_score = s.get("player2", 0)
                                    p2_score = s.get("player1", 0)
                                    reversed_scores.append(f"{p1_score}:{p2_score}")
                                detail_score = ", ".join(reversed_scores)
                                row["results"].append(
                                    {
                                        "win": p2_sets > p1_sets and not is_draw,
                                        "draw": is_draw,
                                        "score": f"{p2_sets}:{p1_sets}",
                                        "detail_score": detail_score,
                                        "sets": scores["sets"],
                                    }
                                )
                        else:
                            row["results"].append(None)
                    else:
                        row["results"].append(None)
            matrix.append(row)

        # 4. 计算积分排名
        rankings = []
        for p in participants:
            stats = {
                "participant_id": p["id"],
                "student_name": p["student_name"],
                "total_points": 0,  # 总分（胜场数）
                "matches_played": 0,  # 场数（只计算有比分的）
                "wins": 0,
                "losses": 0,
                "draws": 0,  # 平局数
                "sets_won": 0,  # 胜负局
                "sets_lost": 0,
                "points_scored": 0,  # 胜负分
                "points_conceded": 0,
            }

            for m in matches:
                if m["player1_id"] == p["id"] or m["player2_id"] == p["id"]:
                    # 只统计有比分的比赛
                    if (
                        m["scores"]
                        and isinstance(m["scores"], dict)
                        and "sets" in m["scores"]
                        and len(m["scores"]["sets"]) > 0
                    ):
                        stats["matches_played"] += 1
                        is_player1 = m["player1_id"] == p["id"]

                        for s in m["scores"]["sets"]:
                            p1_score = s.get("player1", 0)
                            p2_score = s.get("player2", 0)

                            if is_player1:
                                stats["points_scored"] += p1_score
                                stats["points_conceded"] += p2_score
                                if p1_score > p2_score:
                                    stats["sets_won"] += 1
                                elif p2_score > p1_score:
                                    stats["sets_lost"] += 1
                                # 平局时sets_won和sets_lost都不增加
                            else:
                                stats["points_scored"] += p2_score
                                stats["points_conceded"] += p1_score
                                if p2_score > p1_score:
                                    stats["sets_won"] += 1
                                elif p1_score > p2_score:
                                    stats["sets_lost"] += 1

                        # 判断胜负平
                        p1_sets = sum(
                            1
                            for s in m["scores"]["sets"]
                            if s.get("player1", 0) > s.get("player2", 0)
                        )
                        p2_sets = sum(
                            1
                            for s in m["scores"]["sets"]
                            if s.get("player2", 0) > s.get("player1", 0)
                        )

                        if is_player1:
                            if p1_sets > p2_sets:
                                stats["wins"] += 1
                                stats["total_points"] += 1
                            elif p2_sets > p1_sets:
                                stats["losses"] += 1
                            else:
                                stats["draws"] += 1
                                stats["total_points"] += 0.5  # 平局得0.5分
                        else:
                            if p2_sets > p1_sets:
                                stats["wins"] += 1
                                stats["total_points"] += 1
                            elif p1_sets > p2_sets:
                                stats["losses"] += 1
                            else:
                                stats["draws"] += 1
                                stats["total_points"] += 0.5  # 平局得0.5分

            rankings.append(stats)

        # 按总分、胜负局差、胜负分差排序
        rankings.sort(
            key=lambda x: (
                -x["total_points"],
                -(x["sets_won"] - x["sets_lost"]),
                -(x["points_scored"] - x["points_conceded"]),
            )
        )

        # 5. 构建赛程列表
        schedule = []
        for m in matches:
            p1 = participant_map.get(m["player1_id"], {})
            p2 = participant_map.get(m["player2_id"], {})

            score_str = "-"
            if m["scores"] and isinstance(m["scores"], dict) and "sets" in m["scores"]:
                sets = m["scores"]["sets"]
                if sets:
                    # 计算总局数比分
                    p1_sets = sum(
                        1 for s in sets if s.get("player1", 0) > s.get("player2", 0)
                    )
                    p2_sets = sum(
                        1 for s in sets if s.get("player2", 0) > s.get("player1", 0)
                    )
                    score_str = f"{p1_sets}:{p2_sets}"

            # 构建详细比分数据
            sets_data = []
            if m["scores"] and isinstance(m["scores"], dict) and "sets" in m["scores"]:
                for s in m["scores"]["sets"]:
                    sets_data.append(
                        {"player1": s.get("player1", 0), "player2": s.get("player2", 0)}
                    )

            schedule.append(
                {
                    "match_id": m["id"],
                    "player1_id": m["player1_id"],
                    "player1_name": p1.get("student_name", "Unknown"),
                    "player2_id": m["player2_id"],
                    "player2_name": p2.get("student_name", "Unknown"),
                    "score": score_str,
                    "sets": sets_data,
                    "scheduled_time": m["scheduled_time"].isoformat()
                    if m["scheduled_time"]
                    else None,
                    "completed": m["winner_id"] is not None,
                }
            )

        return {"matrix": matrix, "rankings": rankings, "schedule": schedule}
