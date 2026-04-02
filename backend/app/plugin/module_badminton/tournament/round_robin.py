"""
分组循环赛引擎

实现docs/分组循环赛.md中定义的规则：
1. 将参赛者分为若干小组（每组4-5人）
2. 小组内进行单循环赛（每人相互对战）
3. 小组赛结束后，按排名规则确定各小组出线名额
4. 出线者进入交叉淘汰赛

排名优先级：
1. 胜场数
2. 积分（胜场得2分，负场得1分，弃权0分）
3. 相互胜负关系（仅两人间）
4. 净胜局数
5. 净胜分数
6. 抽签
"""

import itertools
import random
from typing import Dict, List, Optional

from .engine.base import (
    Group,
    Match,
    MatchFormat,
    Participant,
    TournamentConfig,
    TournamentEngine,
    TournamentType,
    calculate_ranking_score,
    RoundType,
)


class RoundRobinEngine(TournamentEngine):
    """分组循环赛引擎"""

    def __init__(self, config: TournamentConfig):
        super().__init__(config)
        if config.tournament_type != TournamentType.ROUND_ROBIN:
            raise ValueError("引擎类型不匹配")

    def create_groups(self, participants: List[Participant]) -> List[Group]:
        """
        创建分组

        规则：
        1. 种子选手平均分配到不同小组
        2. 非种子选手抽签入组
        3. 每组4-5人为宜
        """
        self.validate_participants(participants)

        # 对参赛者进行种子排序
        seeded_participants = self.seed_participants(participants)

        # 确定分组数量
        num_groups = self.config.num_groups
        if num_groups is None:
            # 自动计算分组数量（每组4-5人）
            ideal_group_size = self.config.group_size or 4
            num_groups = max(1, len(participants) // ideal_group_size)
            if len(participants) % ideal_group_size > 0:
                num_groups += 1

        # 确定每组人数
        group_size = self.config.group_size
        if group_size is None:
            group_size = len(participants) // num_groups
            remainder = len(participants) % num_groups

        # 创建空分组
        groups = []
        for i in range(num_groups):
            group_name = f"第{i + 1}组"
            groups.append(
                Group(id=i + 1, name=group_name, participants=[], order=i + 1)
            )

        # 分配种子选手
        if self.config.use_seeding:
            for i, participant in enumerate(seeded_participants):
                group_idx = i % num_groups
                groups[group_idx].participants.append(participant)
        else:
            # 随机分配
            random.shuffle(seeded_participants)
            for i, participant in enumerate(seeded_participants):
                group_idx = i % num_groups
                groups[group_idx].participants.append(participant)

        return groups

    def generate_matches(self, groups: List[Group]) -> List[Match]:
        """
        生成对阵表

        规则：
        1. 小组内单循环赛（每个参赛者与其他所有参赛者比赛一次）
        2. 交叉淘汰赛（小组赛结束后生成）
        """
        matches = []
        match_id = 1

        # 第一阶段：小组循环赛
        for group in groups:
            participants = group.participants
            if len(participants) < 2:
                continue

            # 生成所有可能的对阵组合（不重复）
            combinations = list(itertools.combinations(participants, 2))

            for round_num, (player1, player2) in enumerate(combinations, 1):
                match = Match(
                    id=match_id,
                    round_number=1,  # 小组赛为第1轮
                    match_number=round_num,
                    player1_id=player1.id,
                    player2_id=player2.id,
                    player1_name=player1.name,
                    player2_name=player2.name,
                    status="scheduled",
                )
                matches.append(match)
                match_id += 1

        # 第二阶段：交叉淘汰赛（需要小组赛结果后才能生成）
        # 实际生成应在小组赛结束后调用generate_knockout_matches方法
        return matches

    def generate_knockout_matches(
        self, groups: List[Group], group_results: Dict[int, List[Participant]]
    ) -> List[Match]:
        """
        生成交叉淘汰赛对阵表

        参数:
        - groups: 分组列表
        - group_results: 分组ID -> 排名列表的映射

        返回:
        - 淘汰赛比赛列表
        """
        matches = []
        match_id = len(groups) * 10 + 1  # 从较大的ID开始，避免与小组赛冲突

        # 确定出线名额
        advance_from_group = self.config.advance_from_group or 2

        # 收集所有出线选手
        advancing_participants = []
        for group in groups:
            if group.id in group_results:
                rankings = group_results[group.id]
                # 取前N名出线
                advancing = rankings[:advance_from_group]
                advancing_participants.extend(advancing)

        # 如果出线选手数量不是2的幂次，需要轮空
        total_advancing = len(advancing_participants)
        next_power_of_two = 1
        while next_power_of_two < total_advancing:
            next_power_of_two <<= 1

        # 种子排序（按小组排名）
        seeded_participants = sorted(
            advancing_participants, key=lambda p: getattr(p, "group_rank", 999)
        )

        # 生成淘汰赛对阵（标准锦标赛对阵表）
        # 使用标准锦标赛种子对阵：1 vs 8, 2 vs 7, 3 vs 6, 4 vs 5
        for i in range(0, next_power_of_two // 2):
            player1_idx = i
            player2_idx = next_power_of_two - 1 - i

            if player1_idx < len(seeded_participants) and player2_idx < len(
                seeded_participants
            ):
                player1 = seeded_participants[player1_idx]
                player2 = seeded_participants[player2_idx]

                match = Match(
                    id=match_id,
                    round_number=2,  # 淘汰赛第1轮
                    match_number=i + 1,
                    player1_id=player1.id,
                    player2_id=player2.id,
                    player1_name=player1.name,
                    player2_name=player2.name,
                    status="scheduled",
                )
                matches.append(match)
                match_id += 1
            elif player1_idx < len(seeded_participants):
                # player2轮空
                pass

        return matches

    def calculate_rankings(
        self, groups: List[Group], matches: List[Match]
    ) -> Dict[int, List[Participant]]:
        """
        计算小组排名

        排名优先级：
        1. 胜场数
        2. 积分
        3. 相互胜负关系（仅两人间）
        4. 净胜局数
        5. 净胜分数
        6. 抽签
        """
        rankings = {}

        for group in groups:
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
                    "head_to_head": {},  # 与其他选手的胜负关系
                }

            # 计算相互胜负关系
            for match in group_matches:
                if match.winner_id:
                    loser_id = (
                        match.player2_id
                        if match.winner_id == match.player1_id
                        else match.player1_id
                    )

                    if (
                        match.winner_id in participant_stats
                        and loser_id in participant_stats
                    ):
                        # 记录胜负关系
                        if (
                            loser_id
                            not in participant_stats[match.winner_id]["head_to_head"]
                        ):
                            participant_stats[match.winner_id]["head_to_head"][
                                loser_id
                            ] = 0
                        if (
                            match.winner_id
                            not in participant_stats[loser_id]["head_to_head"]
                        ):
                            participant_stats[loser_id]["head_to_head"][
                                match.winner_id
                            ] = 0

                        participant_stats[match.winner_id]["head_to_head"][
                            loser_id
                        ] += 1

            # 排序函数
            def sort_key(pid):
                stats = participant_stats[pid]["stats"]
                return (
                    -stats["wins"],  # 胜场数（降序）
                    -stats["points"],  # 积分（降序）
                    # 相互胜负关系在排序中处理
                    -stats["games_diff"],  # 净胜局数（降序）
                    -stats["points_diff"],  # 净胜分数（降序）
                )

            # 获取排序后的参与者ID
            sorted_pids = sorted(participant_stats.keys(), key=sort_key)

            # 处理相互胜负关系
            # 如果两名选手积分相同，检查他们之间的直接胜负关系
            final_ranking = []
            i = 0
            while i < len(sorted_pids):
                current_pid = sorted_pids[i]
                current_stats = participant_stats[current_pid]["stats"]

                # 查找积分相同的选手
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
                    # 处理积分相同的选手
                    # 按相互胜负关系排序
                    tied_participants = [
                        (pid, participant_stats[pid]) for pid in same_score_group
                    ]

                    # 简单排序：按相互胜负关系（胜场多者排前）
                    def head_to_head_sort(item):
                        pid, data = item
                        # 计算在该小组中的总胜场数
                        total_wins = sum(data["head_to_head"].values())
                        return -total_wins

                    tied_participants.sort(key=head_to_head_sort)

                    for pid, _ in tied_participants:
                        final_ranking.append(participant_stats[pid]["participant"])

                    i += len(same_score_group)

            rankings[group.id] = final_ranking

        return rankings

    def simulate_group_stage(
        self, groups: List[Group], matches: List[Match]
    ) -> List[Match]:
        """
        模拟小组赛（用于测试）

        为每场比赛随机生成比分并确定胜者
        """
        for match in matches:
            if match.status == "scheduled" and match.round_number == 1:
                # 随机决定胜者
                if random.random() > 0.5:
                    match.winner_id = match.player1_id
                else:
                    match.winner_id = match.player2_id

                # 生成随机比分（基于比赛形式）
                if self.config.match_format == MatchFormat.BEST_OF_THREE_21:
                    # 三局两胜，胜者赢2局
                    match.scores = []
                    player1_wins = 0
                    player2_wins = 0

                    for _ in range(3):
                        if player1_wins == 2 or player2_wins == 2:
                            break

                        if match.winner_id == match.player1_id:
                            # player1赢此局
                            if random.random() > 0.3:
                                # 正常比分
                                player1_score = 21
                                player2_score = random.randint(10, 19)
                            else:
                                # 激烈比分
                                player1_score = random.randint(22, 30)
                                player2_score = player1_score - 2
                            player1_wins += 1
                        else:
                            # player2赢此局
                            if random.random() > 0.3:
                                player2_score = 21
                                player1_score = random.randint(10, 19)
                            else:
                                player2_score = random.randint(22, 30)
                                player1_score = player2_score - 2
                            player2_wins += 1

                        match.scores.append((player1_score, player2_score))

                match.status = "completed"

        return matches
