"""
tournament模块 - Schema定义
"""

from datetime import date, datetime, time
from typing import Optional

from fastapi import Query
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
    model_serializer,
)

from app.api.v1.module_system.user.schema import UserOutSchema
from app.core.base_schema import BaseSchema, UserBySchema
from app.core.validator import DateStr, DateTimeStr, TimeStr

from ..enums import TournamentTypeEnum, TournamentStatusEnum

# ============================================================================
# 赛事相关 Schema（基础）
# ============================================================================


class TournamentCreateSchema(BaseModel):
    """赛事创建模型"""

    name: str = Field(..., description="赛事名称")
    tournament_type: TournamentTypeEnum = Field(..., description="赛事类型")
    start_date: DateStr = Field(..., description="开始日期")
    end_date: DateStr = Field(..., description="结束日期")
    registration_deadline: Optional[DateTimeStr] = Field(
        None, description="报名截止时间"
    )
    group_size: Optional[int] = Field(None, description="每组人数")
    num_groups: Optional[int] = Field(None, description="分组数量")
    match_format: Optional[str] = Field(None, description="比赛形式")
    points_per_game: Optional[int] = Field(None, description="每局分数")
    description: Optional[str] = Field(None, description="赛事描述")
    location: Optional[str] = Field(None, description="比赛地点")
    advance_count: Optional[int] = Field(None, description="淘汰赛晋级总人数")
    advance_top_n: Optional[int] = Field(None, description="每组前N名晋级")

    @model_validator(mode="after")
    def validate_championship_params(self) -> "TournamentCreateSchema":
        """校验锦标赛模式参数"""
        if self.tournament_type and self.tournament_type.value == "CHAMPIONSHIP":
            if self.advance_count is None or self.advance_top_n is None:
                raise ValueError("锦标赛模式必须填写晋级人数和前几晋级参数")
            if self.advance_count < 4:
                raise ValueError("晋级人数不能少于4")
            if self.advance_top_n < 1:
                raise ValueError("前几晋级不能少于1")
            if self.advance_count % self.advance_top_n != 0:
                raise ValueError("晋级人数必须能被前几晋级整除")
            # 检查 advance_count 是 2 的幂次
            if self.advance_count & (self.advance_count - 1) != 0:
                raise ValueError("晋级人数必须为2的幂次（4, 8, 16, 32）")
            if self.group_size and self.advance_top_n >= self.group_size:
                raise ValueError("前几晋级必须小于每组人数")
            # 自动计算分组数
            self.num_groups = self.advance_count // self.advance_top_n
        return self

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """验证赛事名称"""
        v = v.strip()
        if not v:
            raise ValueError("赛事名称不能为空")
        if len(v) < 2 or len(v) > 128:
            raise ValueError("赛事名称长度必须在2-128个字符之间")
        return v

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v: DateStr, info) -> DateStr:
        """验证结束日期"""
        start_date = info.data.get("start_date")
        if start_date and v < start_date:
            raise ValueError("结束日期不能早于开始日期")
        return v

    @field_validator("registration_deadline")
    @classmethod
    def validate_registration_deadline(
        cls, v: Optional[DateTimeStr], info
    ) -> Optional[DateTimeStr]:
        """验证报名截止时间"""
        if v is None:
            return v
        start_date = info.data.get("start_date")
        if start_date and v.date() > start_date:
            raise ValueError("报名截止时间不能晚于开始日期")
        return v


class TournamentUpdateSchema(TournamentCreateSchema):
    """赛事更新模型"""

    name: Optional[str] = Field(None, description="赛事名称")
    tournament_type: Optional[TournamentTypeEnum] = Field(None, description="赛事类型")
    start_date: Optional[DateStr] = Field(None, description="开始日期")
    end_date: Optional[DateStr] = Field(None, description="结束日期")


class TournamentOutSchema(TournamentCreateSchema, BaseSchema, UserBySchema):
    """赛事响应模型"""

    status: TournamentStatusEnum = Field(
        default=TournamentStatusEnum.DRAFT, description="赛事状态"
    )

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class SetScoreSchema(BaseModel):
    """单局比分模型"""

    player1: int = Field(..., description="选手1得分")
    player2: int = Field(..., description="选手2得分")


class MatchScoreSchema(BaseModel):
    """比赛比分模型"""

    sets: list[SetScoreSchema] = Field(..., description="局数列表")


class ParticipantUpdateSchema(BaseModel):
    """参赛队员更新模型"""

    seed_rank: Optional[int] = Field(None, description="种子排名")


class BatchAddParticipantsSchema(BaseModel):
    """批量添加参赛队员模型"""

    student_ids: list[int] = Field(..., description="学员ID列表")
