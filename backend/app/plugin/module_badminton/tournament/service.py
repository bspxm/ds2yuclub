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
from .crud import *
from .schema import *

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
        cls, auth: AuthSchema, tournament_id: int, data: TournamentCreateSchema
    ) -> dict:
        """更新赛事"""
        tournament = await TournamentCRUD(auth).get_by_id_crud(tournament_id)
        if not tournament:
            raise CustomException(msg="赛事不存在")

        # 如果赛事已开始，不能修改某些字段
        if tournament.status != "draft":
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
        """获取赛事列表"""
        tournaments = await TournamentCRUD(auth).list_crud(
            order_by=[{"start_date": "desc"}], preload=["created_by", "updated_by"]
        )
        return [
            TournamentOutSchema.model_validate(tournament).model_dump()
            for tournament in tournaments
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
        from app.core.database import async_session

        async with async_session() as session:
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

            result = await session.execute(stmt)
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
                "student1_wins": sum(
                    1 for r in records if r["winner_id"] == student_id_1
                ),
                "student2_wins": sum(
                    1 for r in records if r["winner_id"] == student_id_2
                ),
                "records": records,
            }


class TournamentParticipantService:
    """参赛队员服务层"""

    @classmethod
    async def batch_add_service(
        cls, tournament_id: int, student_ids: list[int], auth: AuthSchema
    ) -> list[dict]:
        """批量添加参赛队员"""
        tournament = await TournamentCRUD(auth).get_by_id_crud(tournament_id)
        if not tournament:
            raise CustomException(msg="赛事不存在")

        if tournament.status != "draft":
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
        """获取赛事参赛队员列表"""
        participants = await TournamentParticipantCRUD(auth).get_by_tournament_crud(
            tournament_id
        )
        return [
            {
                "id": p.id,
                "student_id": p.student_id,
                "student_name": p.student.name if p.student else "",
                "seed_rank": p.seed_rank,
                "group_id": p.group_id,
                "group_name": p.group.group_name if p.group else None,
                "matches_played": p.matches_played,
                "wins": p.matches_won,
                "losses": p.matches_lost,
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

        if tournament.status != "draft":
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
        tournament = await TournamentCRUD(auth).get_by_id_crud(
            tournament_id, preload=["participants"]
        )
        if not tournament:
            raise CustomException(msg="赛事不存在")

        if not tournament.participants:
            raise CustomException(msg="没有参赛队员")

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

        participants = [
            Participant(
                id=p.id,
                name=p.student.name if p.student else f"Player {p.student_id}",
                seed_rank=p.seed_rank,
            )
            for p in tournament.participants
        ]

        groups = engine.create_groups(participants)
        matches = engine.generate_matches(groups)

        created_matches = []
        for m in matches:
            match_model = TournamentMatchModel(
                tournament_id=tournament_id,
                round_type=m.round_type.value,
                round_number=m.round_number,
                match_number=m.match_number,
                player1_id=m.player1_id,
                player2_id=m.player2_id,
                status="scheduled",
            )
            from app.core.database import async_session

            async with async_session() as session:
                session.add(match_model)
                await session.commit()
                await session.refresh(match_model)
                created_matches.append(
                    {
                        "id": match_model.id,
                        "round_number": match_model.round_number,
                        "match_number": match_model.match_number,
                        "player1_id": match_model.player1_id,
                        "player2_id": match_model.player2_id,
                        "round_type": match_model.round_type,
                        "status": match_model.status,
                    }
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
        """获取对阵列表"""
        tournament = await TournamentCRUD(auth).get_by_id_crud(
            tournament_id, preload=["matches", "participants"]
        )
        if not tournament:
            raise CustomException(msg="赛事不存在")

        matches = tournament.matches

        if group_id:
            matches = [m for m in matches if m.group_id == group_id]

        if round_type:
            matches = [m for m in matches if m.round_type == round_type]

        participant_map = {p.id: p for p in tournament.participants}

        return [
            {
                "id": m.id,
                "round_number": m.round_number,
                "match_number": m.match_number,
                "round_type": m.round_type,
                "status": m.status,
                "player1": {
                    "id": m.player1_id,
                    "student_name": participant_map[m.player1_id].student.name
                    if participant_map[m.player1_id].student
                    else "",
                }
                if m.player1_id in participant_map
                else None,
                "player2": {
                    "id": m.player2_id,
                    "student_name": participant_map[m.player2_id].student.name
                    if participant_map[m.player2_id].student
                    else "",
                }
                if m.player2_id in participant_map
                else None,
                "scores": m.scores,
                "winner_id": m.winner_id,
            }
            for m in sorted(matches, key=lambda x: (x.round_number, x.match_number))
        ]

    @classmethod
    async def get_match_detail_service(
        cls, tournament_id: int, match_id: int, auth: AuthSchema
    ) -> dict:
        """获取比赛详情"""
        from app.core.database import async_session

        async with async_session() as session:
            from sqlalchemy import select

            stmt = select(TournamentMatchModel).where(
                TournamentMatchModel.id == match_id,
                TournamentMatchModel.tournament_id == tournament_id,
            )
            result = await session.execute(stmt)
            m = result.scalar_one_or_none()

            if not m:
                raise CustomException(msg="比赛不存在")

            return {
                "id": m.id,
                "tournament_id": m.tournament_id,
                "round_number": m.round_number,
                "match_number": m.match_number,
                "round_type": m.round_type,
                "status": m.status,
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
        """录入比分"""
        from app.core.database import async_session

        async with async_session() as session:
            from sqlalchemy import select

            stmt = select(TournamentMatchModel).where(
                TournamentMatchModel.id == match_id,
                TournamentMatchModel.tournament_id == tournament_id,
            )
            result = await session.execute(stmt)
            m = result.scalar_one_or_none()

            if not m:
                raise CustomException(msg="比赛不存在")

            if m.status == "completed":
                raise CustomException(msg="比赛已完成，无法修改比分")

            scores_data = {
                "sets": [
                    {"player1": s.player1, "player2": s.player2} for s in scores.sets
                ]
            }
            m.scores = scores_data

            p1_score = sum(s.player1 for s in scores.sets)
            p2_score = sum(s.player2 for s in scores.sets)

            p1_wins = sum(1 for s in scores.sets if s.player1 > s.player2)
            p2_wins = sum(1 for s in scores.sets if s.player2 > s.player1)

            wins_needed = 2
            if p1_wins >= wins_needed:
                m.winner_id = m.player1_id
            elif p2_wins >= wins_needed:
                m.winner_id = m.player2_id

            m.status = "completed"

            await session.commit()

            return {
                "id": m.id,
                "scores": m.scores,
                "winner_id": m.winner_id,
                "status": m.status,
            }
