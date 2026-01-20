"""
比赛引擎抽象基类

定义所有赛制引擎的通用接口，支持4种赛制：
1. 分组循环赛（带淘汰赛）
2. 纯小组赛
3. 定区升降赛
4. 小组单败制淘汰赛

每种赛制需实现以下核心功能：
- 分组策略
- 对阵生成
- 比分处理
- 排名计算
"""

import enum
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel


class TournamentType(str, enum.Enum):
    """赛制类型枚举"""
    ROUND_ROBIN = "round_robin"            # 分组循环赛（带淘汰赛）
    PURE_GROUP = "pure_group"              # 纯小组赛
    PROMOTION_RELEGATION = "promotion_relegation"  # 定区升降赛
    SINGLE_ELIMINATION = "single_elimination"      # 小组单败制淘汰赛


class MatchFormat(str, enum.Enum):
    """比赛形式枚举"""
    BEST_OF_THREE_21 = "best_of_three_21"  # 三局两胜21分制
    BEST_OF_FIVE_21 = "best_of_five_21"    # 五局三胜21分制
    ONE_GAME_31 = "one_game_31"            # 一局31分制
    ONE_GAME_15 = "one_game_15"            # 一局15分制（定区升降赛常用）


@dataclass
class Participant:
    """参赛者数据类"""
    id: int
    name: str
    seed_rank: Optional[int] = None  # 种子排名
    level: Optional[str] = None      # 水平等级
    metadata: Dict[str, Any] = None  # 扩展元数据
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Group:
    """分组数据类"""
    id: int
    name: str
    participants: List[Participant]
    order: int = 0  # 组序


@dataclass
class Match:
    """比赛数据类"""
    id: int
    round_number: int
    match_number: int
    player1_id: int
    player2_id: int
    player1_name: str = ""
    player2_name: str = ""
    scheduled_time: Optional[str] = None
    status: str = "scheduled"  # scheduled, in_progress, completed, cancelled
    scores: Optional[List[Tuple[int, int]]] = None  # 每局比分 [(21,19), (19,21), (21,17)]
    winner_id: Optional[int] = None
    
    def add_score(self, player1_score: int, player2_score: int):
        """添加一局比分"""
        if self.scores is None:
            self.scores = []
        self.scores.append((player1_score, player2_score))
    
    def determine_winner(self, match_format: MatchFormat) -> Optional[int]:
        """根据比分确定胜者（基于比赛形式）"""
        if not self.scores:
            return None
        
        if match_format == MatchFormat.ONE_GAME_31 or match_format == MatchFormat.ONE_GAME_15:
            # 一局定胜负
            player1_score, player2_score = self.scores[0]
            return self.player1_id if player1_score > player2_score else self.player2_id
        
        # 多局制比赛（三局两胜或五局三胜）
        wins_needed = 2 if match_format == MatchFormat.BEST_OF_THREE_21 else 3
        player1_wins = 0
        player2_wins = 0
        
        for player1_score, player2_score in self.scores:
            if player1_score > player2_score:
                player1_wins += 1
            else:
                player2_wins += 1
            
            if player1_wins >= wins_needed:
                return self.player1_id
            if player2_wins >= wins_needed:
                return self.player2_id
        
        return None


@dataclass
class TournamentConfig:
    """赛事配置"""
    tournament_type: TournamentType
    match_format: MatchFormat = MatchFormat.BEST_OF_THREE_21
    points_per_game: int = 21  # 每局分数
    group_size: Optional[int] = None  # 每组人数
    num_groups: Optional[int] = None  # 分组数量
    advance_from_group: int = 2  # 每组出线人数（淘汰赛用）
    use_seeding: bool = True    # 是否使用种子排名


@dataclass
class TournamentResult:
    """赛事结果"""
    groups: List[Group]
    matches: List[Match]
    rankings: Dict[int, List[Participant]]  # group_id -> 排名列表


class TournamentEngine(ABC):
    """比赛引擎抽象基类"""
    
    def __init__(self, config: TournamentConfig):
        self.config = config
    
    @abstractmethod
    def create_groups(self, participants: List[Participant]) -> List[Group]:
        """
        创建分组
        
        参数:
        - participants: 参赛者列表
        
        返回:
        - 分组列表
        """
        pass
    
    @abstractmethod
    def generate_matches(self, groups: List[Group]) -> List[Match]:
        """
        生成对阵表
        
        参数:
        - groups: 分组列表
        
        返回:
        - 比赛列表
        """
        pass
    
    @abstractmethod
    def calculate_rankings(self, groups: List[Group], matches: List[Match]) -> Dict[int, List[Participant]]:
        """
        计算排名
        
        参数:
        - groups: 分组列表
        - matches: 比赛列表
        
        返回:
        - 分组ID到排名列表的映射
        """
        pass
    
    def validate_participants(self, participants: List[Participant]) -> bool:
        """验证参赛者数据"""
        if not participants:
            raise ValueError("参赛者列表不能为空")
        
        if len(participants) < 2:
            raise ValueError("至少需要2名参赛者")
        
        # 检查ID唯一性
        participant_ids = [p.id for p in participants]
        if len(participant_ids) != len(set(participant_ids)):
            raise ValueError("参赛者ID必须唯一")
        
        return True
    
    def seed_participants(self, participants: List[Participant]) -> List[Participant]:
        """对参赛者进行种子排序"""
        # 按种子排名排序，无种子排名的放在后面
        seeded = [p for p in participants if p.seed_rank is not None]
        unseeded = [p for p in participants if p.seed_rank is None]
        
        seeded.sort(key=lambda x: x.seed_rank)
        # 将未排名的参赛者随机分配到种子选手后面
        # 这里简单地将未排名选手追加到列表末尾
        return seeded + unseeded


class TournamentEngineFactory:
    """比赛引擎工厂"""
    
    @staticmethod
    def create_engine(tournament_type: TournamentType, **kwargs) -> TournamentEngine:
        """
        创建比赛引擎
        
        参数:
        - tournament_type: 赛制类型
        - **kwargs: 引擎配置参数
        
        返回:
        - 比赛引擎实例
        """
        config = TournamentConfig(tournament_type=tournament_type, **kwargs)
        
        if tournament_type == TournamentType.ROUND_ROBIN:
            from .round_robin import RoundRobinEngine
            return RoundRobinEngine(config)
        elif tournament_type == TournamentType.PURE_GROUP:
            from .pure_group import PureGroupEngine
            return PureGroupEngine(config)
        elif tournament_type == TournamentType.PROMOTION_RELEGATION:
            from .promotion_relegation import PromotionRelegationEngine
            return PromotionRelegationEngine(config)
        elif tournament_type == TournamentType.SINGLE_ELIMINATION:
            from .single_elimination import SingleEliminationEngine
            return SingleEliminationEngine(config)
        else:
            raise ValueError(f"不支持的赛制类型: {tournament_type}")


# 通用工具函数
def calculate_match_points(score: Tuple[int, int]) -> Tuple[int, int]:
    """
    计算比赛积分（根据羽毛球规则）
    
    胜场得2分，负场得1分，弃权0分
    
    返回:
    - (player1_points, player2_points)
    """
    player1_score, player2_score = score
    
    if player1_score == 0 and player2_score == 0:
        # 双方弃权
        return (0, 0)
    elif player1_score > player2_score:
        return (2, 1)
    elif player2_score > player1_score:
        return (1, 2)
    else:
        # 平局（理论上羽毛球比赛不会平局，但保留处理）
        return (1, 1)


def calculate_ranking_score(participant: Participant, matches: List[Match]) -> Dict[str, Any]:
    """
    计算参赛者排名分数（用于排名比较）
    
    返回包含以下指标的字典：
    - 胜场数
    - 积分
    - 净胜局数
    - 净胜分数
    """
    wins = 0
    points = 0
    games_won = 0
    games_lost = 0
    points_scored = 0
    points_conceded = 0
    
    for match in matches:
        if match.winner_id == participant.id:
            wins += 1
            points += 2
        elif match.player1_id == participant.id or match.player2_id == participant.id:
            # 参赛但输了
            points += 1
        
        # 计算局分和分数
        if match.scores and (match.player1_id == participant.id or match.player2_id == participant.id):
            for player1_score, player2_score in match.scores:
                if match.player1_id == participant.id:
                    games_won += 1 if player1_score > player2_score else 0
                    games_lost += 1 if player1_score < player2_score else 0
                    points_scored += player1_score
                    points_conceded += player2_score
                else:
                    games_won += 1 if player2_score > player1_score else 0
                    games_lost += 1 if player2_score < player1_score else 0
                    points_scored += player2_score
                    points_conceded += player1_score
    
    return {
        "wins": wins,
        "points": points,
        "games_diff": games_won - games_lost,
        "points_diff": points_scored - points_conceded,
        "games_won": games_won,
        "games_lost": games_lost,
        "points_scored": points_scored,
        "points_conceded": points_conceded,
    }