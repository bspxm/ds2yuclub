"""
纯小组赛引擎

实现docs/分组循环赛（纯小组赛）.md中定义的规则：
1. 按水平分组（每组4-6人）
2. 小组内单循环赛
3. 直接按循环赛成绩决定最终名次

排名优先级：
1. 胜场数
2. 净胜局数（若采用多局制）
3. 净胜分数
4. 直接胜负关系（仅两人）
5. 抽签

注意：多人积分相同时，优先比较净胜分而非胜负关系（更公平）
"""

from typing import Dict, List

from .engine.base import (
    Group,
    Match,
    Participant,
    TournamentConfig,
    TournamentEngine,
    TournamentType,
)


class PureGroupEngine(TournamentEngine):
    """纯小组赛引擎"""

    def __init__(self, config: TournamentConfig):
        super().__init__(config)
        if config.tournament_type != TournamentType.PURE_GROUP:
            raise ValueError("引擎类型不匹配")

    def create_groups(self, participants: List[Participant]) -> List[Group]:
        """创建分组（按水平分组）"""
        self.validate_participants(participants)

        # TODO: 实现按水平分组逻辑
        # 1. 如果有水平等级信息，按水平分组
        # 2. 种子选手平均分布
        # 3. 每组4-6人

        groups = []
        # 临时实现：简单分为一组
        groups.append(Group(id=1, name="全体", participants=participants, order=1))
        return groups

    def generate_matches(self, groups: List[Group]) -> List[Match]:
        """生成对阵表（小组内单循环）"""
        matches = []
        # TODO: 实现单循环对阵生成
        return matches

    def calculate_rankings(
        self, groups: List[Group], matches: List[Match]
    ) -> Dict[int, List[Participant]]:
        """
        计算排名

        特殊规则：多人积分相同时，优先比较净胜分而非胜负关系
        """
        rankings = {}
        # TODO: 实现纯小组赛排名算法
        return rankings
