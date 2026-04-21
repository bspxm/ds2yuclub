"""
tournament模块 - CRUD数据操作层
"""

from typing import Optional, List, Dict, Any, Sequence, Sequence

from app.api.v1.module_system.auth.schema import AuthSchema
from app.core.base_crud import CRUDBase
from app.core.database import SessionDep
from app.core.logger import logger

from .model import *
from .schema import TournamentCreateSchema, TournamentUpdateSchema
from ..enums import MatchStatusEnum

# ============================================================================
# 赛事 CRUD
# ============================================================================


class TournamentCRUD(
    CRUDBase[TournamentModel, TournamentCreateSchema, TournamentUpdateSchema]
):
    """赛事数据层"""

    def __init__(self, auth: AuthSchema) -> None:
        super().__init__(model=TournamentModel, auth=auth)

    async def get_by_id_crud(
        self, id: int, preload: Optional[list[str]] = None
    ) -> Optional[TournamentModel]:
        """获取赛事详情"""
        logger.info(f"[get_by_id_crud] 查询赛事详情，id={id}, preload={preload}")
        result = await self.get(id=id, preload=preload)
        if result:
            logger.info(
                f"[get_by_id_crud] 找到赛事：id={result.id}, name={result.name}"
            )
        else:
            logger.warning(f"[get_by_id_crud] 未找到赛事，id={id}")
        return result

    async def list_crud(
        self,
        search: Optional[dict] = None,
        order_by: Optional[list[dict]] = None,
        preload: Optional[list[str]] = None,
    ) -> Sequence[TournamentModel]:
        """赛事列表"""
        return await self.list(search=search, order_by=order_by, preload=preload)

    async def create_crud(
        self, data: TournamentCreateSchema
    ) -> Optional[TournamentModel]:
        """创建赛事"""
        # 将schema转换为字典
        obj_dict = data.model_dump()

        # 处理日期字段：将字符串转换为date对象
        date_fields = ["start_date", "end_date"]
        for field in date_fields:
            if field in obj_dict and obj_dict[field] is not None:
                value = obj_dict[field]
                if isinstance(value, str):
                    # 字符串转换为date对象
                    try:
                        obj_dict[field] = datetime.strptime(value, "%Y-%m-%d").date()
                    except ValueError:
                        # 如果格式不匹配，尝试其他格式或保持原样
                        pass

        # 传递字典给基类的create方法
        return await self.create(data=obj_dict)

    async def update_crud(
        self, id: int, data: TournamentUpdateSchema
    ) -> Optional[TournamentModel]:
        """更新赛事"""
        # 将schema转换为字典
        obj_dict = data.model_dump(exclude_unset=True, exclude={"id"})

        # 处理枚举字段：将枚举对象转换为字符串值
        for key, value in obj_dict.items():
            if hasattr(value, "value"):
                obj_dict[key] = value.value

        # 处理日期字段：将字符串转换为date对象
        date_fields = ["start_date", "end_date"]
        for field in date_fields:
            if field in obj_dict and obj_dict[field] is not None:
                value = obj_dict[field]
                if isinstance(value, str):
                    # 字符串转换为date对象
                    try:
                        obj_dict[field] = datetime.strptime(value, "%Y-%m-%d").date()
                    except ValueError:
                        # 如果格式不匹配，尝试其他格式或保持原样
                        pass

        # 传递字典给基类的update方法
        return await self.update(id=id, data=obj_dict)

    async def delete_crud(self, ids: list[int]) -> None:
        """删除赛事"""
        return await self.delete(ids=ids)

    async def update_status_crud(
        self, tournament_id: int, status: str
    ) -> Optional[TournamentModel]:
        """更新赛事状态"""
        return await self.update(id=tournament_id, data={"status": status})

    async def get_active_tournaments_crud(self) -> Sequence[TournamentModel]:
        """获取进行中的赛事"""
        return await self.list(
            search={"status": ("eq", "active")}, order_by=[{"start_date": "asc"}]
        )

    async def page_crud(
        self,
        offset: int,
        limit: int,
        order_by: list[dict[str, str]],
        search: dict,
        out_schema: type,
        preload: list[str] | None = None,
    ) -> dict:
        """赛事分页查询"""
        return await self.page(
            offset=offset,
            limit=limit,
            order_by=order_by,
            search=search,
            out_schema=out_schema,
            preload=preload,
        )


# ============================================================================
# 参赛学员 CRUD
# ============================================================================


class TournamentParticipantCRUD(CRUDBase[TournamentParticipantModel, dict, dict]):
    """参赛学员数据层（使用通用schema）"""

    def __init__(self, auth: AuthSchema) -> None:
        super().__init__(model=TournamentParticipantModel, auth=auth)

    async def register_crud(
        self, tournament_id: int, student_id: int, seed_rank: Optional[int] = None
    ) -> Optional[TournamentParticipantModel]:
        """学员报名参赛"""
        # 检查是否已报名
        existing = await self.get(tournament_id=tournament_id, student_id=student_id)
        if existing:
            raise ValueError("该学员已报名此赛事")

        data = {
            "tournament_id": tournament_id,
            "student_id": student_id,
            "seed_rank": seed_rank,
            "is_withdrawn": False,
        }
        return await self.create(data=data)

    async def withdraw_crud(
        self, participant_id: int
    ) -> Optional[TournamentParticipantModel]:
        """学员退赛"""
        return await self.update(participant_id, {"is_withdrawn": True})

    async def get_by_tournament_crud(self, tournament_id: int) -> list[dict]:
        """获取赛事所有参赛者 - 使用统计视图优化查询"""
        from sqlalchemy import text

        sql = text("""
            SELECT 
                id,
                student_id,
                student_name,
                age,
                group_name,
                level,
                seed_rank,
                final_rank,
                group_id,
                matches_played,
                wins as matches_won,
                losses as matches_lost
            FROM v_tournament_participant_stats
            WHERE tournament_id = :tournament_id
            ORDER BY seed_rank NULLS LAST, id
        """)

        result = await self.auth.db.execute(sql, {"tournament_id": tournament_id})
        rows = result.mappings().all()

        return [dict(row) for row in rows]

    async def get_by_tournament_with_position_crud(
        self, tournament_id: int
    ) -> list[dict]:
        """获取赛事参赛者（带抢位赛位置信息）"""
        from sqlalchemy import text

        sql = text("""
            SELECT
                p.id as participant_id,
                p.student_id,
                s.name as student_name,
                p.current_position,
                p.seed_rank
            FROM badminton_tournament_participant p
            JOIN badminton_student s ON p.student_id = s.id
            WHERE p.tournament_id = :tournament_id
            AND p.is_withdrawn = false
            ORDER BY p.current_position NULLS LAST, p.id
        """)

        result = await self.auth.db.execute(sql, {"tournament_id": tournament_id})
        rows = result.mappings().all()
        return [dict(row) for row in rows]

    async def init_positions_crud(
        self, tournament_id: int
    ) -> list[dict]:
        """随机抽签初始化位置"""
        from sqlalchemy import text
        import random

        # 获取所有参赛者
        sql = text("""
            SELECT id FROM badminton_tournament_participant
            WHERE tournament_id = :tournament_id
            AND is_withdrawn = false
        """)
        result = await self.auth.db.execute(sql, {"tournament_id": tournament_id})
        participant_ids = [row[0] for row in result.fetchall()]

        if len(participant_ids) < 2:
            raise CustomException(msg="参赛人数不足，无法初始化位置")

        # 随机打乱
        random.shuffle(participant_ids)

        # 批量更新位置
        updates = []
        for i, pid in enumerate(participant_ids):
            updates.append(f"({pid}, {i + 1})")

        update_sql = text(f"""
            UPDATE badminton_tournament_participant AS p
            SET current_position = v.pos
            FROM (VALUES {', '.join(updates)}) AS v(id, pos)
            WHERE p.id = v.id
        """)
        await self.auth.db.execute(update_sql)
        await self.auth.db.flush()

        return await self.get_by_tournament_with_position_crud(tournament_id)

    async def swap_positions_crud(
        self, participant_id_1: int, participant_id_2: int
    ) -> None:
        """交换两个参赛者的位置"""
        from sqlalchemy import text

        # 获取当前位置
        sql = text("""
            SELECT id, current_position FROM badminton_tournament_participant
            WHERE id IN (:id1, :id2)
        """)
        result = await self.auth.db.execute(sql, {"id1": participant_id_1, "id2": participant_id_2})
        rows = result.fetchall()

        if len(rows) != 2:
            raise CustomException(msg="参赛者不存在")

        positions = {row[0]: row[1] for row in rows}
        pos1 = positions[participant_id_1]
        pos2 = positions[participant_id_2]

        # 交换
        swap_sql = text("""
            UPDATE badminton_tournament_participant
            SET current_position = CASE
                WHEN id = :id1 THEN :pos2 ::integer
                WHEN id = :id2 THEN :pos1 ::integer
            END
            WHERE id IN (:id1, :id2)
        """)
        await self.auth.db.execute(
            swap_sql,
            {"id1": participant_id_1, "id2": participant_id_2, "pos1": pos1, "pos2": pos2},
        )
        await self.auth.db.flush()

    async def update_statistics_crud(
        self, participant_id: int, won: bool, points_scored: int, points_conceded: int
    ) -> Optional[TournamentParticipantModel]:
        """更新参赛者统计信息"""
        participant = await self.get(id=participant_id)
        if not participant:
            return None

        participant.matches_played += 1
        if won:
            participant.matches_won += 1
        else:
            participant.matches_lost += 1

        participant.total_points_scored += points_scored
        participant.total_points_conceded += points_conceded

        return await self.update(
            participant_id,
            {
                "matches_played": participant.matches_played,
                "matches_won": participant.matches_won,
                "matches_lost": participant.matches_lost,
                "total_points_scored": participant.total_points_scored,
                "total_points_conceded": participant.total_points_conceded,
            },
        )


class TournamentMatchCRUD(CRUDBase[TournamentMatchModel, dict, dict]):
    """比赛对阵数据层（使用通用schema）"""

    def __init__(self, auth: AuthSchema) -> None:
        super().__init__(model=TournamentMatchModel, auth=auth)

    async def create_match_crud(
        self,
        tournament_id: int,
        round_type: str,
        round_number: int,
        match_number: int,
        player1_id: int,
        player2_id: int,
        group_id: Optional[int] = None,
    ) -> Optional[TournamentMatchModel]:
        """创建比赛对阵"""
        data = {
            "tournament_id": tournament_id,
            "round_type": round_type,
            "round_number": round_number,
            "match_number": match_number,
            "player1_id": player1_id,
            "player2_id": player2_id,
            "status": MatchStatusEnum.SCHEDULED,
        }
        if group_id is not None:
            data["group_id"] = group_id

        result = await self.create(data=data)
        if not result:
            logger.error(
                f"[create_match_crud] 对阵创建失败: tournament_id={tournament_id}, player1_id={player1_id}, player2_id={player2_id}"
            )
        return result

    async def get_by_tournament_crud(
        self, tournament_id: int, group_id: Optional[int] = None
    ) -> Sequence[TournamentMatchModel]:
        """获取赛事所有比赛"""
        logger.info(
            f"[get_by_tournament_crud] 查询对阵: tournament_id={tournament_id}, group_id={group_id}"
        )
        search = {"tournament_id": ("eq", tournament_id)}
        if group_id:
            search["group_id"] = ("eq", group_id)

        result = await self.list(
            search=search,
            order_by=[{"round_number": "asc"}, {"match_number": "asc"}],
            preload=["player1", "player2"],
        )
        logger.info(f"[get_by_tournament_crud] 查询到{len(result)}个对阵记录")
        return result

    async def update_score_crud(
        self, match_id: int, scores: dict, winner_id: int, status: str = "COMPLETED"
    ) -> dict:
        """更新比赛比分 - 使用直接SQL避免关联加载，返回基本字段"""
        import time
        from sqlalchemy import update

        start = time.time()

        # 直接执行UPDATE，使用RETURNING返回基本字段
        stmt = (
            update(TournamentMatchModel)
            .where(TournamentMatchModel.id == match_id)
            .values(
                scores=scores,
                winner_id=winner_id,
                status=status,
            )
            .returning(
                TournamentMatchModel.id,
                TournamentMatchModel.scores,
                TournamentMatchModel.winner_id,
                TournamentMatchModel.status,
            )
        )

        step1 = time.time()
        result = await self.auth.db.execute(stmt)
        row = result.fetchone()
        step2 = time.time()

        print(
            f"[update_score_crud] 构建SQL: {step1 - start:.4f}s, 执行UPDATE: {step2 - step1:.4f}s"
        )

        if row:
            # 将枚举类型转换为字符串
            status_value = row[3]
            if hasattr(status_value, "value"):
                status_value = status_value.value
            return {
                "id": row[0],
                "scores": row[1],
                "winner_id": row[2],
                "status": status_value,
            }
        return None


class TournamentGroupCRUD(CRUDBase[TournamentGroupModel, dict, dict]):
    """赛事分组数据层"""

    def __init__(self, auth: AuthSchema) -> None:
        super().__init__(model=TournamentGroupModel, auth=auth)

    async def create_group_crud(
        self,
        tournament_id: int,
        group_order: int,
        group_name: str,
    ) -> Optional[TournamentGroupModel]:
        """创建分组"""
        data = {
            "tournament_id": tournament_id,
            "group_order": group_order,
            "group_name": group_name,
        }
        result = await self.create(data=data)
        if not result:
            logger.error(
                f"[create_group_crud] 分组创建失败: tournament_id={tournament_id}, group_order={group_order}"
            )
        return result
