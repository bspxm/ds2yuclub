"""
tournament模块 - CRUD数据操作层
"""

from typing import Optional, List, Dict, Any, Sequence, Sequence

from app.api.v1.module_system.auth.schema import AuthSchema
from app.core.base_crud import CRUDBase
from app.core.database import SessionDep

from .model import *
from .schema import TournamentCreateSchema, TournamentUpdateSchema

# ============================================================================
# 赛事 CRUD
# ============================================================================

class TournamentCRUD(CRUDBase[TournamentModel, TournamentCreateSchema, TournamentUpdateSchema]):
    """赛事数据层"""

    def __init__(self, auth: AuthSchema) -> None:
        super().__init__(model=TournamentModel, auth=auth)

    async def get_by_id_crud(self, id: int, preload: Optional[list[str]] = None) -> Optional[TournamentModel]:
        """获取赛事详情"""
        return await self.get(id=id, preload=preload)

    async def list_crud(self, search: Optional[dict] = None, order_by: Optional[list[dict]] = None, preload: Optional[list[str]] = None) -> Sequence[TournamentModel]:
        """赛事列表"""
        return await self.list(search=search, order_by=order_by, preload=preload)

    async def create_crud(self, data: TournamentCreateSchema) -> Optional[TournamentModel]:
        """创建赛事"""
        # 将schema转换为字典
        obj_dict = data.model_dump()
        
        # 处理日期字段：将字符串转换为date对象
        date_fields = ['start_date', 'end_date']
        for field in date_fields:
            if field in obj_dict and obj_dict[field] is not None:
                value = obj_dict[field]
                if isinstance(value, str):
                    # 字符串转换为date对象
                    try:
                        obj_dict[field] = datetime.strptime(value, '%Y-%m-%d').date()
                    except ValueError:
                        # 如果格式不匹配，尝试其他格式或保持原样
                        pass
        
        # 传递字典给基类的create方法
        return await self.create(data=obj_dict)

    async def update_crud(self, id: int, data: TournamentUpdateSchema) -> Optional[TournamentModel]:
        """更新赛事"""
        # 将schema转换为字典
        obj_dict = data.model_dump(exclude_unset=True, exclude={"id"})
        
        # 处理日期字段：将字符串转换为date对象
        date_fields = ['start_date', 'end_date']
        for field in date_fields:
            if field in obj_dict and obj_dict[field] is not None:
                value = obj_dict[field]
                if isinstance(value, str):
                    # 字符串转换为date对象
                    try:
                        obj_dict[field] = datetime.strptime(value, '%Y-%m-%d').date()
                    except ValueError:
                        # 如果格式不匹配，尝试其他格式或保持原样
                        pass
        
        # 传递字典给基类的update方法
        return await self.update(id=id, data=obj_dict)

    async def delete_crud(self, ids: list[int]) -> None:
        """删除赛事"""
        return await self.delete(ids=ids)

    async def update_status_crud(self, tournament_id: int, status: str) -> Optional[TournamentModel]:
        """更新赛事状态"""
        return await self.update_crud(tournament_id, TournamentUpdateSchema(status=status))

    async def get_active_tournaments_crud(self) -> Sequence[TournamentModel]:
        """获取进行中的赛事"""
        return await self.list(
            search={"status": ("eq", "active")},
            order_by=[{"start_date": "asc"}]
        )

    async def page_crud(self, offset: int, limit: int, order_by: list[dict[str, str]], search: dict, out_schema: type, preload: list[str] | None = None) -> dict:
        """赛事分页查询"""
        return await self.page(offset=offset, limit=limit, order_by=order_by, search=search, out_schema=out_schema, preload=preload)

# ============================================================================
# 参赛学员 CRUD
# ============================================================================

class TournamentParticipantCRUD(CRUDBase[TournamentParticipantModel, dict, dict]):
    """参赛学员数据层（使用通用schema）"""

    def __init__(self, auth: AuthSchema) -> None:
        super().__init__(model=TournamentParticipantModel, auth=auth)

    async def register_crud(self, tournament_id: int, student_id: int, seed_rank: Optional[int] = None) -> Optional[TournamentParticipantModel]:
        """学员报名参赛"""
        # 检查是否已报名
        existing = await self.get(tournament_id=tournament_id, student_id=student_id)
        if existing:
            raise ValueError("该学员已报名此赛事")
        
        data = {
            "tournament_id": tournament_id,
            "student_id": student_id,
            "seed_rank": seed_rank,
            "is_withdrawn": False
        }
        return await self.create(data=data)

    async def withdraw_crud(self, participant_id: int) -> Optional[TournamentParticipantModel]:
        """学员退赛"""
        return await self.update(participant_id, {"is_withdrawn": True})

    async def get_by_tournament_crud(self, tournament_id: int) -> Sequence[TournamentParticipantModel]:
        """获取赛事所有参赛者"""
        return await self.list(
            search={"tournament_id": ("eq", tournament_id), "is_withdrawn": ("eq", False)},
            preload=["student", "group"]
        )

    async def update_statistics_crud(self, participant_id: int, won: bool, points_scored: int, points_conceded: int) -> Optional[TournamentParticipantModel]:
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
        
        return await self.update(participant_id, {
            "matches_played": participant.matches_played,
            "matches_won": participant.matches_won,
            "matches_lost": participant.matches_lost,
            "total_points_scored": participant.total_points_scored,
            "total_points_conceded": participant.total_points_conceded
        })
