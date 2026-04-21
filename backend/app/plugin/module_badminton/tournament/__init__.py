"""
羽毛球比赛引擎模块

提供单败淘汰赛对阵生成和比分管理
"""

# 数据模型
from .model import (
    TournamentModel,
    TournamentGroupModel,
    TournamentParticipantModel,
    TournamentMatchModel,
)

# 服务
from .service import (
    TournamentService,
    TournamentParticipantService,
    TournamentMatchService,
)

# 淘汰赛服务
from .knockout_service import KnockoutService

__all__ = [
    # 数据模型
    "TournamentModel",
    "TournamentGroupModel",
    "TournamentParticipantModel",
    "TournamentMatchModel",
    # 服务
    "TournamentService",
    "TournamentParticipantService",
    "TournamentMatchService",
    "KnockoutService",
]
