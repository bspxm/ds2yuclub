"""
定区升降赛引擎

实现docs/定区升降赛.md中定义的规则：
1. 设置固定位置（如1号冠军位、2号位……末位）
2. 选手随机抽签或按水平入位
3. 低位选手发起挑战高位相邻选手
4. 挑战者获胜则双方交换位置，否则位置不变
5. 重复挑战直至时间结束或达成目标

特殊规则：
- 1号位只能被2号位挑战
- 通常采用一局定胜负（15/21/11分）加快节奏
- 刚比赛过的选手下一轮暂免挑战
"""

from typing import Dict, List

from .engine import Group, Match, Participant, TournamentConfig, TournamentEngine


class PromotionRelegationEngine(TournamentEngine):
    """定区升降赛引擎"""
    
    def __init__(self, config: TournamentConfig):
        super().__init__(config)
        if config.tournament_type != TournamentType.PROMOTION_RELEGATION:
            raise ValueError("引擎类型不匹配")
    
    def create_groups(self, participants: List[Participant]) -> List[Group]:
        """创建位置分组"""
        self.validate_participants(participants)
        
        # 在定区升降赛中，每个位置都是一个"分组"
        # 但实际上我们只需要一个组包含所有选手，并记录他们的位置
        groups = []
        # 创建位置列表，按种子排名或随机分配位置
        positioned_participants = self.assign_positions(participants)
        groups.append(Group(id=1, name="位置赛", participants=positioned_participants, order=1))
        return groups
    
    def generate_matches(self, groups: List[Group]) -> List[Match]:
        """生成挑战对阵"""
        matches = []
        # TODO: 实现挑战对阵生成逻辑
        # 1. 根据当前位置生成可能的挑战
        # 2. 考虑"刚比赛过的选手暂免挑战"规则
        return matches
    
    def calculate_rankings(self, groups: List[Group], matches: List[Match]) -> Dict[int, List[Participant]]:
        """计算最终位置排名"""
        rankings = {}
        # 最终排名就是比赛结束时的位置顺序
        # TODO: 实现位置排名计算
        return rankings
    
    def assign_positions(self, participants: List[Participant]) -> List[Participant]:
        """分配初始位置"""
        # 按种子排名分配位置，第1种子到1号位，第2种子到2号位，依此类推
        seeded = self.seed_participants(participants)
        # 为每个参与者添加位置属性
        for i, participant in enumerate(seeded):
            participant.metadata['position'] = i + 1
            participant.metadata['can_be_challenged'] = True
        return seeded
    
    def get_valid_challenges(self, participants: List[Participant], recent_matches: List[Match]) -> List[tuple]:
        """获取有效的挑战对"""
        valid_challenges = []
        # TODO: 实现挑战合法性检查
        # 1. 低位可以挑战高位相邻选手
        # 2. 1号位只能被2号位挑战
        # 3. 刚比赛过的选手不能立即被挑战
        return valid_challenges