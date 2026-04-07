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
from .crud import (
    TournamentCRUD,
    TournamentParticipantCRUD,
    TournamentMatchCRUD,
    TournamentGroupCRUD,
)
from .schema import *
from .knockout_service import KnockoutService
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
                "advance_count": row.get("advance_count"),
                "advance_top_n": row.get("advance_top_n"),
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
        from sqlalchemy import text

        for tournament_id in ids:
            # 使用原生SQL快速查询状态和存在性
            result = await auth.db.execute(
                text("SELECT id, status FROM badminton_tournament WHERE id = :id"),
                {"id": tournament_id},
            )
            row = result.fetchone()
            if not row:
                raise CustomException(msg="赛事不存在")
            if row.status != "DRAFT":
                raise CustomException(msg="非草稿状态的赛事不能删除")

        # 使用原生SQL删除，数据库级联会自动处理关联数据
        await auth.db.execute(
            text("DELETE FROM badminton_tournament WHERE id = ANY(:ids)"), {"ids": ids}
        )
        await auth.db.commit()

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
            select(
                TournamentModel.id,
                TournamentModel.status,
                TournamentModel.num_groups,
                TournamentModel.group_size,
            ).where(TournamentModel.id == tournament_id)
        )
        tournament = result.first()

        if not tournament:
            raise CustomException(msg="赛事不存在")

        if tournament.status != TournamentStatusEnum.DRAFT:
            raise CustomException(msg="赛事已开始，不能添加参赛队员")

        # 验证参赛人数是否超过容量
        max_participants = (tournament.num_groups or 1) * (tournament.group_size or 4)

        # 获取当前参赛人数
        current_count_result = await auth.db.execute(
            text(
                "SELECT COUNT(*) FROM badminton_tournament_participant WHERE tournament_id = :tid"
            ),
            {"tid": tournament_id},
        )
        current_count = current_count_result.scalar() or 0

        # 计算添加后总人数
        new_count = current_count + len(student_ids)
        if new_count > max_participants:
            raise CustomException(
                msg=f"参赛人数超出限制：当前{current_count}人，最大容量{max_participants}人（{tournament.num_groups}组×{tournament.group_size}人/组）"
            )

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
            f"[generate_matches_service] 赛事名称={tournament.name}, 类型={tournament.tournament_type.value}, 参赛人数={len(tournament.participants)}"
        )

        # 过滤掉没有关联学员的参赛者
        valid_participants = [
            p for p in tournament.participants if p.student_id is not None
        ]
        if len(valid_participants) != len(tournament.participants):
            logger.warning(
                f"[generate_matches_service] 过滤掉 {len(tournament.participants) - len(valid_participants)} 个无效参赛者"
            )

        if len(valid_participants) < 2:
            raise CustomException(msg="有效参赛人数不足")

        # 单败淘汰赛使用淘汰赛服务
        if tournament.tournament_type.value == "SINGLE_ELIMINATION":
            logger.info("[generate_matches_service] 使用淘汰赛服务生成对阵表")
            participant_ids = [p.id for p in valid_participants]
            result = await KnockoutService.generate_bracket(
                tournament_id=tournament_id, participant_ids=participant_ids, auth=auth
            )
            return result.get("matches", [])

        # 小组循环赛
        elif tournament.tournament_type.value in [
            "ROUND_ROBIN",
            "PURE_GROUP",
            "CHAMPIONSHIP",
        ]:
            logger.info("[generate_matches_service] 使用循环赛算法生成对阵表")
            # 清除旧的分组和比赛数据
            await cls._cleanup_old_group_data(tournament_id, auth)
            return await cls._generate_round_robin_matches(
                tournament_id, tournament, auth
            )

        # 其他赛制暂不支持
        else:
            logger.warning(
                f"[generate_matches_service] 暂不支持的赛制类型: {tournament.tournament_type.value}"
            )
            return []

    @classmethod
    async def _cleanup_old_group_data(
        cls, tournament_id: int, auth: AuthSchema
    ) -> None:
        """清除旧的分组和比赛数据，重置参赛者的group_id"""
        from sqlalchemy import text

        # 重置参赛者的 group_id
        await auth.db.execute(
            text(
                "UPDATE badminton_tournament_participant SET group_id = NULL WHERE tournament_id = :tid"
            ),
            {"tid": tournament_id},
        )
        # 删除旧的比赛
        await auth.db.execute(
            text("DELETE FROM badminton_tournament_match WHERE tournament_id = :tid"),
            {"tid": tournament_id},
        )
        # 删除旧的分组
        await auth.db.execute(
            text("DELETE FROM badminton_tournament_group WHERE tournament_id = :tid"),
            {"tid": tournament_id},
        )
        await auth.db.flush()
        logger.info(f"[cleanup_old_group_data] 已清除赛事 {tournament_id} 的旧分组数据")

    @classmethod
    async def _generate_round_robin_matches(
        cls, tournament_id: int, tournament, auth: AuthSchema
    ) -> list[dict]:
        """生成小组循环赛对阵表（并行优化版）"""
        from itertools import combinations
        import asyncio

        participants = tournament.participants
        num_participants = len(participants)

        # 分组 - 根据 group_size 自动计算分组数
        group_size = tournament.group_size or 4
        num_groups = (num_participants + group_size - 1) // group_size

        # 分离种子选手和非种子选手
        seeded = [p for p in participants if p.seed_rank is not None]
        unseeded = [p for p in participants if p.seed_rank is None]

        # 种子选手按排名排序
        seeded_sorted = sorted(seeded, key=lambda p: p.seed_rank)

        # 非种子选手随机打乱
        import random

        random.shuffle(unseeded)

        # 初始化分组
        groups = [[] for _ in range(num_groups)]

        # 先分配种子选手：每组分配一个种子（按种子排名顺序）
        for i, p in enumerate(seeded_sorted):
            group_idx = i % num_groups
            groups[group_idx].append(p)

        # 再分配非种子选手：蛇形分配到各组
        for i, p in enumerate(unseeded):
            group_idx = i % num_groups
            if i // num_groups % 2 == 1:
                group_idx = num_groups - 1 - group_idx
            groups[group_idx].append(p)

        # 创建分组（并行）
        group_crud = TournamentGroupCRUD(auth)
        participant_crud = TournamentParticipantCRUD(auth)
        match_crud = TournamentMatchCRUD(auth)

        # 并行创建所有分组
        group_tasks = [
            group_crud.create_group_crud(
                tournament_id=tournament_id,
                group_order=group_idx + 1,
                group_name=f"第{group_idx + 1}组",
            )
            for group_idx in range(num_groups)
        ]
        group_models = await asyncio.gather(*group_tasks)
        group_id_map = {
            group_idx: model.id for group_idx, model in enumerate(group_models)
        }

        # 并行更新所有参赛者的 group_id
        participant_tasks = []
        for group_idx, group in enumerate(groups):
            group_id = group_id_map[group_idx]
            for p in group:
                participant_tasks.append(
                    participant_crud.update(p.id, {"group_id": group_id})
                )
        await asyncio.gather(*participant_tasks)

        # 并行创建所有比赛
        match_tasks = []
        match_number = 1
        for group_idx, group in enumerate(groups):
            for p1, p2 in combinations(group, 2):
                match_tasks.append(
                    match_crud.create_match_crud(
                        tournament_id=tournament_id,
                        round_type="GROUP_STAGE",
                        round_number=1,
                        match_number=match_number,
                        player1_id=p1.id,
                        player2_id=p2.id,
                        group_id=group_id_map[group_idx],
                    )
                )
                match_number += 1

        match_models = await asyncio.gather(*match_tasks)

        # 构建返回结果
        created_matches = [
            {
                "id": model.id,
                "round_number": model.round_number,
                "match_number": model.match_number,
                "player1_id": model.player1_id,
                "player2_id": model.player2_id,
                "round_type": "GROUP_STAGE",
                "status": model.status.value,
                "group_id": model.group_id,
            }
            for model in match_models
            if model
        ]

        logger.info(
            f"[generate_matches_service] 循环赛生成完成，共{len(created_matches)}场比赛"
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
        """获取羽球在线风格的小组赛数据 - 按小组组织"""
        from sqlalchemy import text

        # 获取赛事类型（用于排名算法分支）
        tournament_type_sql = text("""
            SELECT tournament_type FROM badminton_tournament WHERE id = :tid
        """)
        t_result = await auth.db.execute(tournament_type_sql, {"tid": tournament_id})
        t_row = t_result.mappings().first()
        tournament_type = t_row["tournament_type"] if t_row else None

        # 1. 获取赛事的所有分组
        groups_sql = text("""
            SELECT 
                g.id,
                g.group_name,
                g.group_order
            FROM badminton_tournament_group g
            WHERE g.tournament_id = :tournament_id
            ORDER BY g.group_order
        """)

        result = await auth.db.execute(groups_sql, {"tournament_id": tournament_id})
        db_groups = result.mappings().all()

        if not db_groups:
            return {"groups": []}

        # 2. 获取每个分组内的选手
        groups_data = []
        for group in db_groups:
            # 如果指定了特定分组，只返回该分组数据
            if group_id and group["id"] != group_id:
                continue

            group_participants_sql = text("""
                SELECT 
                    p.id,
                    p.student_id,
                    s.name as student_name,
                    p.seed_rank
                FROM badminton_tournament_participant p
                JOIN badminton_student s ON p.student_id = s.id
                WHERE p.group_id = :group_id
                AND p.is_withdrawn = false
                ORDER BY p.seed_rank NULLS LAST, p.id
            """)

            result = await auth.db.execute(
                group_participants_sql, {"group_id": group["id"]}
            )
            participants = result.mappings().all()

            if not participants:
                groups_data.append(
                    {
                        "id": group["id"],
                        "name": group["group_name"],
                        "data": {"matrix": [], "rankings": [], "schedule": []},
                    }
                )
                continue

            participant_ids = [p["id"] for p in participants]
            participant_map = {p["id"]: p for p in participants}

            # 3. 获取该分组的所有比赛
            matches_sql = text("""
                SELECT 
                    m.id,
                    m.player1_id,
                    m.player2_id,
                    m.scores,
                    m.winner_id,
                    m.scheduled_time
                FROM badminton_tournament_match m
                WHERE m.group_id = :group_id
                AND m.round_type = 'GROUP_STAGE'
                ORDER BY m.scheduled_time
            """)

            result = await auth.db.execute(matches_sql, {"group_id": group["id"]})
            matches = result.mappings().all()

            # 4. 构建该分组的对阵矩阵
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
                                m["player1_id"] == p1["id"]
                                and m["player2_id"] == p2["id"]
                            ) or (
                                m["player1_id"] == p2["id"]
                                and m["player2_id"] == p1["id"]
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

            # 5. 计算该分组的积分排名
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

            if tournament_type == "CHAMPIONSHIP":
                # 锦标赛排名：胜场数 → 净胜局数 → 净胜分数（无平局）
                rankings.sort(
                    key=lambda x: (
                        -x["wins"],
                        -(x["sets_won"] - x["sets_lost"]),
                        -(x["points_scored"] - x["points_conceded"]),
                    )
                )
            else:
                # 其他赛制排名：总分 → 净胜局 → 净胜分
                rankings.sort(
                    key=lambda x: (
                        -x["total_points"],
                        -(x["sets_won"] - x["sets_lost"]),
                        -(x["points_scored"] - x["points_conceded"]),
                    )
                )

            # 6. 构建该分组的赛程列表
            schedule = []
            for m in matches:
                p1 = participant_map.get(m["player1_id"], {})
                p2 = participant_map.get(m["player2_id"], {})

                score_str = "-"
                if (
                    m["scores"]
                    and isinstance(m["scores"], dict)
                    and "sets" in m["scores"]
                ):
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
                if (
                    m["scores"]
                    and isinstance(m["scores"], dict)
                    and "sets" in m["scores"]
                ):
                    for s in m["scores"]["sets"]:
                        sets_data.append(
                            {
                                "player1": s.get("player1", 0),
                                "player2": s.get("player2", 0),
                            }
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

            groups_data.append(
                {
                    "id": group["id"],
                    "name": group["group_name"],
                    "data": {
                        "matrix": matrix,
                        "rankings": rankings,
                        "schedule": schedule,
                    },
                }
            )

        return {"groups": groups_data}

    @classmethod
    async def _generate_championship_knockout(
        cls, tournament_id: int, auth: AuthSchema
    ) -> dict:
        """锦标赛模式：根据小组赛排名生成淘汰赛对阵"""
        from sqlalchemy import text

        # 1. 获取赛事信息
        tournament = await TournamentCRUD(auth).get_by_id_crud(tournament_id)
        if not tournament:
            raise CustomException(msg="赛事不存在")
        if tournament.tournament_type.value != "CHAMPIONSHIP":
            raise CustomException(msg="仅锦标赛模式支持此操作")

        advance_count = tournament.advance_count
        advance_top_n = tournament.advance_top_n
        if not advance_count or not advance_top_n:
            raise CustomException(msg="锦标赛参数缺失")

        # 2. 检查所有小组赛是否已完成
        incomplete_sql = text("""
            SELECT COUNT(*) as cnt
            FROM badminton_tournament_match
            WHERE tournament_id = :tournament_id
            AND round_type = 'GROUP_STAGE'
            AND status != 'COMPLETED'
        """)
        result = await auth.db.execute(incomplete_sql, {"tournament_id": tournament_id})
        incomplete_count = result.scalar()
        if incomplete_count and incomplete_count > 0:
            raise CustomException(
                msg=f"还有 {incomplete_count} 场小组赛未完成，请先完成所有小组赛"
            )

        # 3. 获取小组赛排名数据
        group_stage_data = await cls.get_group_stage_data_service(
            tournament_id, None, auth
        )

        if not group_stage_data.get("groups"):
            raise CustomException(msg="小组赛数据为空")

        # 4. 收集晋级选手（按淘汰赛种子顺序排列）
        # 策略：先收集各组第1名，再收集各组第2名...
        # 这样淘汰赛对阵时自然实现交叉排位
        # 例如 4组 top2=2: A1, B1, C1, D1, A2, B2, C2, D2
        # KnockoutService 种子对阵 1v8(A1 vs D2), 2v7(B1 vs C2)...
        advancing_participants = []
        groups = group_stage_data["groups"]

        for rank_idx in range(advance_top_n):
            for group_data in groups:
                rankings = group_data["data"]["rankings"]
                if rank_idx < len(rankings):
                    advancing_participants.append(rankings[rank_idx])

        # 5. 获取晋级选手的 participant ID
        participant_ids = [p["participant_id"] for p in advancing_participants]

        if len(participant_ids) < 2:
            raise CustomException(msg="晋级人数不足")

        # 6. 删除已有的淘汰赛对阵（如果有）
        await auth.db.execute(
            text(
                "DELETE FROM badminton_tournament_match WHERE tournament_id = :tid AND round_type = 'KNOCKOUT'"
            ),
            {"tid": tournament_id},
        )
        await auth.db.flush()

        # 7. 调用 KnockoutService 生成淘汰赛对阵
        result = await KnockoutService.generate_bracket(
            tournament_id=tournament_id,
            participant_ids=participant_ids,
            auth=auth,
        )

        return {
            "advancing_count": len(participant_ids),
            "knockout_matches": result.get("matches", []),
            "total_rounds": result.get("total_rounds", 0),
        }

    @classmethod
    async def get_championship_status(
        cls, tournament_id: int, auth: AuthSchema
    ) -> dict:
        """获取锦标赛两阶段状态概览"""
        from sqlalchemy import text

        # 小组赛统计
        group_sql = text("""
            SELECT
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE status = 'COMPLETED') as completed
            FROM badminton_tournament_match
            WHERE tournament_id = :tournament_id
            AND round_type = 'GROUP_STAGE'
        """)
        group_result = await auth.db.execute(
            group_sql, {"tournament_id": tournament_id}
        )
        group_row = group_result.fetchone()

        # 淘汰赛统计
        knockout_sql = text("""
            SELECT
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE status = 'COMPLETED') as completed
            FROM badminton_tournament_match
            WHERE tournament_id = :tournament_id
            AND round_type = 'KNOCKOUT'
        """)
        knockout_result = await auth.db.execute(
            knockout_sql, {"tournament_id": tournament_id}
        )
        knockout_row = knockout_result.fetchone()

        group_total = group_row.total if group_row else 0
        group_completed = group_row.completed if group_row else 0
        knockout_total = knockout_row.total if knockout_row else 0
        knockout_completed = knockout_row.completed if knockout_row else 0

        return {
            "group_stage": {
                "total": group_total,
                "completed": group_completed,
                "remaining": (group_total or 0) - (group_completed or 0),
                "is_completed": group_total > 0 and group_completed == group_total,
            },
            "knockout": {
                "total": knockout_total,
                "completed": knockout_completed,
                "remaining": (knockout_total or 0) - (knockout_completed or 0),
                "is_generated": knockout_total > 0,
                "is_completed": knockout_total > 0
                and knockout_completed == knockout_total,
            },
        }
