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

import itertools
from typing import Dict, List

from .engine.base import (
    Group,
    Match,
    Participant,
    TournamentConfig,
    TournamentEngine,
    TournamentType,
    RoundType,
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
        match_id = 1

        for group in groups:
            participants = group.participants
            if len(participants) < 2:
                continue

            # 生成所有可能的对阵组合（不重复）
            combinations = list(itertools.combinations(participants, 2))

            for match_num, (player1, player2) in enumerate(combinations, 1):
                match = Match(
                    id=match_id,
                    round_number=1,  # 小组赛为第1轮
                    match_number=match_num,
                    player1_id=player1.id,
                    player2_id=player2.id,
                    player1_name=player1.name,
                    player2_name=player2.name,
                    round_type=RoundType.GROUP_STAGE,
                    status="scheduled",
                )
                matches.append(match)
                match_id += 1

        return matches

    def calculate_rankings(
        self, groups: List[Group], matches: List[Match]
    ) -> Dict[int, List[Participant]]:
        """
        计算排名

        特殊规则：多人积分相同时，优先比较净胜分而非胜负关系
        """
        from .engine.base import calculate_ranking_score

        rankings = {}

        for group in groups:
            # 筛选该小组的比赛
            group_matches = [
                m
                for m in matches
                if (
                    m.player1_id in [p.id for p in group.participants]
                    or m.player2_id in [p.id for p in group.participants]
                )
            ]

            # 计算每个参赛者的统计数据
            participant_stats = {}
            for participant in group.participants:
                stats = calculate_ranking_score(participant, group_matches)
                participant_stats[participant.id] = {
                    "participant": participant,
                    "stats": stats,
                }

            # 排序函数 - 纯小组赛规则：胜场数 > 积分 > 净胜局数 > 净胜分数 > 直接胜负关系
            def sort_key(pid):
                stats = participant_stats[pid]["stats"]
                return (
                    -stats["wins"],        # 胜场数（降序）
                    -stats["points"],      # 积分（降序）
                    -stats["games_diff"],  # 净胜局数（降序）
                    -stats["points_diff"], # 净胜分数（降序）
                    # 直接胜负关系在积分相同时处理
                )

            # 获取排序后的参与者ID
            sorted_pids = sorted(participant_stats.keys(), key=sort_key)

            # 处理积分相同的选手（多人积分相同时，优先比较净胜分而非胜负关系）
            final_ranking = []
            i = 0
            while i < len(sorted_pids):
                current_pid = sorted_pids[i]
                current_stats = participant_stats[current_pid]["stats"]

                # 查找胜场数和积分都相同的选手
                same_score_group = [current_pid]
                j = i + 1
                while j < len(sorted_pids):
                    next_pid = sorted_pids[j]
                    next_stats = participant_stats[next_pid]["stats"]

                    if (
                        current_stats["wins"] == next_stats["wins"]
                        and current_stats["points"] == next_stats["points"]
                    ):
                        same_score_group.append(next_pid)
                        j += 1
                    else:
                        break

                if len(same_score_group) == 1:
                    # 没有积分相同的选手
                    final_ranking.append(participant_stats[current_pid]["participant"])
                    i += 1
                else:
                    # 处理积分相同的选手：按净胜分数排序
                    tied_participants = [
                        (pid, participant_stats[pid]) for pid in same_score_group
                    ]

                    # 按净胜分数降序排序
                    def points_diff_sort(item):
                        pid, data = item
                        return -data["stats"]["points_diff"]

                    tied_participants.sort(key=points_diff_sort)

                    for pid, _ in tied_participants:
                        final_ranking.append(participant_stats[pid]["participant"])

                    i += len(same_score_group)

            rankings[group.id] = final_ranking

        return rankings
