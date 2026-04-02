"""
羽毛球比赛引擎模块

提供4种赛制的比赛引擎：
1. 分组循环赛（带淘汰赛）
2. 纯小组赛
3. 定区升降赛
4. 小组单败制淘汰赛
"""

from .engine import (
    RoundType,
    MatchFormat,
    Participant,
    Group,
    Match,
    TournamentConfig,
    TournamentEngine,
)

# 数据模型
from .model import (
    TournamentModel,
    TournamentGroupModel,
    TournamentParticipantModel,
    TournamentMatchModel,
)

__all__ = [
    # 基础类
    "RoundType",
    "MatchFormat",
    "Participant",
    "Group",
    "Match",
    "TournamentConfig",
    "TournamentEngine",
    # 数据模型
    "TournamentModel",
    "TournamentGroupModel",
    "TournamentParticipantModel",
    "TournamentMatchModel",
]
