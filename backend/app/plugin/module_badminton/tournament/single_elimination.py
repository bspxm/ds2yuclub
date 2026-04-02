"""
小组单败制淘汰赛引擎

实现docs/小组单败制淘汰赛.md中定义的规则：
1. 先进行小组单循环赛，生成种子排名
2. 根据小组人数（3-6人）套用固定对阵表
3. 进行单败淘汰赛，包括半决赛、决赛、排名赛
4. 根据淘汰赛最终落位确定所有名次

内置对阵表模板：
- 4人小组：1vs4，2vs3 → 胜者争冠，负者争季
- 5人小组：4vs5（资格赛）→ 胜者vs1，2vs3 → 后续晋级
- 6人小组：3vs6，4vs5（资格赛）→ 胜者分别vs1和2 → 多轮排名赛
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


class SingleEliminationEngine(TournamentEngine):
    """小组单败制淘汰赛引擎"""

    def __init__(self, config: TournamentConfig):
        super().__init__(config)
        if config.tournament_type != TournamentType.SINGLE_ELIMINATION:
            raise ValueError("引擎类型不匹配")

    def create_groups(self, participants: List[Participant]) -> List[Group]:
        """创建小组（通常只有一个组）"""
        self.validate_participants(participants)

        # 在单败淘汰赛中，通常只有一个小组进行循环赛确定种子排名
        groups = []
        groups.append(Group(id=1, name="小组", participants=participants, order=1))
        return groups

    def generate_matches(self, groups: List[Group]) -> List[Match]:
        """生成淘汰赛对阵表"""
        matches = []

        if not groups:
            return matches

        group = groups[0]
        participants = group.participants
        num_participants = len(participants)

        # 根据人数选择对应的对阵表模板
        bracket_matches = self.generate_bracket(participants, num_participants)
        matches.extend(bracket_matches)

        return matches

    def calculate_rankings(
        self, groups: List[Group], matches: List[Match]
    ) -> Dict[int, List[Participant]]:
        """计算最终名次（根据淘汰赛落位）"""
        rankings = {}
        # TODO: 实现淘汰赛名次计算
        # 根据淘汰赛树状图确定所有名次
        return rankings

    def generate_bracket(
        self, participants: List[Participant], num_participants: int
    ) -> List[Match]:
        """生成对应人数的淘汰赛对阵表"""
        matches = []

        # 首先进行种子排名（假设已通过小组循环赛完成）
        seeded_participants = self.seed_participants(participants)

        if num_participants == 3:
            # 3人小组：1号种子轮空，2vs3，胜者与1争冠
            matches.append(
                self.create_match(seeded_participants[1], seeded_participants[2], 1, 1)
            )
            # 决赛（假设第一场胜者）
            # 需要动态生成，这里只生成第一轮

        elif num_participants == 4:
            # 4人小组：1vs4，2vs3
            matches.append(
                self.create_match(seeded_participants[0], seeded_participants[3], 1, 1)
            )
            matches.append(
                self.create_match(seeded_participants[1], seeded_participants[2], 1, 2)
            )
            # 决赛和季军赛需要根据结果动态生成

        elif num_participants == 5:
            # 5人小组：4vs5（资格赛），胜者vs1，2vs3
            matches.append(
                self.create_match(seeded_participants[3], seeded_participants[4], 1, 1)
            )  # 资格赛
            # 后续比赛需要动态生成

        elif num_participants == 6:
            # 6人小组：3vs6，4vs5（资格赛）
            matches.append(
                self.create_match(seeded_participants[2], seeded_participants[5], 1, 1)
            )
            matches.append(
                self.create_match(seeded_participants[3], seeded_participants[4], 1, 2)
            )
            # 后续比赛需要动态生成

        else:
            # 默认使用标准单败淘汰赛
            next_power_of_two = 1
            while next_power_of_two < num_participants:
                next_power_of_two <<= 1

            for i in range(0, next_power_of_two // 2):
                player1_idx = i
                player2_idx = next_power_of_two - 1 - i

                if player1_idx < num_participants and player2_idx < num_participants:
                    matches.append(
                        self.create_match(
                            seeded_participants[player1_idx],
                            seeded_participants[player2_idx],
                            1,
                            i + 1,
                        )
                    )

        return matches

    def create_match(
        self, player1: Participant, player2: Participant, round_num: int, match_num: int
    ) -> Match:
        """创建比赛对象"""
        return Match(
            id=len(self._match_counter) + 1
            if hasattr(self, "_match_counter")
            else match_num,
            round_number=round_num,
            match_number=match_num,
            player1_id=player1.id,
            player2_id=player2.id,
            player1_name=player1.name,
            player2_name=player2.name,
            status="scheduled",
        )
