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
    async def create_service(cls, auth: AuthSchema, data: TournamentCreateSchema) -> dict:
        """创建赛事"""
        tournament = await TournamentCRUD(auth).create_crud(data=data)
        return TournamentOutSchema.model_validate(tournament).model_dump()

    @classmethod
    async def update_service(cls, auth: AuthSchema, tournament_id: int, data: TournamentCreateSchema) -> dict:
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
    async def update_status_service(cls, auth: AuthSchema, tournament_id: int, status: str) -> dict:
        """更新赛事状态"""
        tournament = await TournamentCRUD(auth).update_status_crud(tournament_id, status)
        if not tournament:
            raise CustomException(msg="赛事不存在")
        return TournamentOutSchema.model_validate(tournament).model_dump()

    @classmethod
    async def list_service(cls, auth: AuthSchema) -> list[dict]:
        """获取赛事列表"""
        tournaments = await TournamentCRUD(auth).list_crud(
            order_by=[{"start_date": "desc"}],
            preload=["created_by", "updated_by"]
        )
        return [TournamentOutSchema.model_validate(tournament).model_dump() for tournament in tournaments]

    @classmethod
    async def get_active_service(cls, auth: AuthSchema) -> list[dict]:
        """获取进行中的赛事"""
        tournaments = await TournamentCRUD(auth).get_active_tournaments_crud()
        return [TournamentOutSchema.model_validate(tournament).model_dump() for tournament in tournaments]
