"""
羽毛球比赛引擎模块

提供4种赛制的比赛引擎：
1. 分组循环赛（带淘汰赛）
2. 纯小组赛
3. 定区升降赛
4. 小组单败制淘汰赛
"""

from .engine import (
    MatchFormat, Participant, Group, Match, TournamentConfig,
    TournamentResult, TournamentType, TournamentEngine, TournamentEngineFactory,
    calculate_match_points, calculate_ranking_score
)

from .round_robin import RoundRobinEngine
from .pure_group import PureGroupEngine
from .promotion_relegation import PromotionRelegationEngine
from .single_elimination import SingleEliminationEngine

# 数据模型
from .model import (
    TournamentModel,
    TournamentGroupModel,
    TournamentParticipantModel,
    TournamentMatchModel
)

# 业务层
from .service import TournamentService

__all__ = [
    # 基础类
    'MatchFormat', 'Participant', 'Group', 'Match', 'TournamentConfig',
    'TournamentResult', 'TournamentType', 'TournamentEngine', 'TournamentEngineFactory',
    'calculate_match_points', 'calculate_ranking_score',

    # 具体引擎
    'RoundRobinEngine',
    'PureGroupEngine',
    'PromotionRelegationEngine',
    'SingleEliminationEngine',

    # 数据模型
    'TournamentModel',
    'TournamentGroupModel',
    'TournamentParticipantModel',
    'TournamentMatchModel',

    # 业务层
    'TournamentService',
]