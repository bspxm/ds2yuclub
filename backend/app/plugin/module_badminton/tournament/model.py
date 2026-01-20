from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, Boolean, Date, DateTime, Enum, ForeignKey, Integer, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import ModelMixin, UserMixin
from ..enums import TournamentTypeEnum, TournamentStatusEnum, MatchStatusEnum

if TYPE_CHECKING:
    from ..student.model import StudentModel


class TournamentModel(ModelMixin, UserMixin):
    """
    赛事模型
    """
    __tablename__: str = 'badminton_tournament'
    __table_args__: dict[str, str] = ({'comment': '赛事表'})
    __loader_options__: list[str] = ["groups", "created_by", "updated_by"]

    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="赛事名称")
    tournament_type: Mapped[TournamentTypeEnum] = mapped_column(
        Enum(TournamentTypeEnum),
        nullable=False,
        comment="赛事类型（赛制）"
    )
    status: Mapped[TournamentStatusEnum] = mapped_column(
        Enum(TournamentStatusEnum),
        default=TournamentStatusEnum.DRAFT,
        nullable=False,
        comment="赛事状态"
    )
    
    # 时间信息
    start_date: Mapped[date] = mapped_column(Date, nullable=False, comment="开始日期")
    end_date: Mapped[date] = mapped_column(Date, nullable=False, comment="结束日期")
    registration_deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="报名截止时间")
    
    # 赛制参数
    max_participants: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="最大参赛人数")
    group_size: Mapped[int | None] = mapped_column(SmallInteger, nullable=True, comment="每组人数")
    num_groups: Mapped[int | None] = mapped_column(SmallInteger, nullable=True, comment="分组数量")
    match_format: Mapped[str | None] = mapped_column(String(32), nullable=True, comment="比赛形式（如三局两胜）")
    points_per_game: Mapped[int | None] = mapped_column(SmallInteger, nullable=True, comment="每局分数（如21分）")
    
    # 描述信息
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="赛事描述")
    location: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="比赛地点")
    
    # 关联关系
    groups: Mapped[list["TournamentGroupModel"]] = relationship(
        back_populates="tournament",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    participants: Mapped[list["TournamentParticipantModel"]] = relationship(
        back_populates="tournament",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    matches: Mapped[list["TournamentMatchModel"]] = relationship(
        back_populates="tournament",
        lazy="selectin",
        cascade="all, delete-orphan"
    )


class TournamentGroupModel(ModelMixin):
    """
    赛事分组模型
    """
    __tablename__: str = 'badminton_tournament_group'
    __table_args__: dict[str, str] = ({'comment': '赛事分组表'})
    __loader_options__: list[str] = ["tournament", "participants", "matches"]

    tournament_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('badminton_tournament.id', ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
        comment="赛事ID"
    )
    group_name: Mapped[str] = mapped_column(String(64), nullable=False, comment="组名")
    group_order: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment="组序")
    
    # 关联关系
    tournament: Mapped["TournamentModel"] = relationship(
        back_populates="groups",
        foreign_keys=[tournament_id],
        lazy="selectin"
    )
    participants: Mapped[list["TournamentParticipantModel"]] = relationship(
        back_populates="group",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    matches: Mapped[list["TournamentMatchModel"]] = relationship(
        back_populates="group",
        lazy="selectin",
        cascade="all, delete-orphan"
    )


class TournamentParticipantModel(ModelMixin):
    """
    参赛学员模型
    """
    __tablename__: str = 'badminton_tournament_participant'
    __table_args__: dict[str, str] = ({'comment': '参赛学员表'})
    __loader_options__: list[str] = ["tournament", "group", "student"]

    tournament_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('badminton_tournament.id', ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
        comment="赛事ID"
    )
    group_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey('badminton_tournament_group.id', ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        index=True,
        comment="分组ID"
    )
    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('badminton_student.id', ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
        comment="学员ID"
    )
    
    # 参赛信息
    seed_rank: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="种子排名")
    final_rank: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="最终排名")
    is_withdrawn: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否退赛")
    
    # 统计信息（实时更新）
    matches_played: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="已赛场次")
    matches_won: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="胜场")
    matches_lost: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="负场")
    total_points_scored: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="总得分")
    total_points_conceded: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="总失分")
    
    # 关联关系
    tournament: Mapped["TournamentModel"] = relationship(
        back_populates="participants",
        foreign_keys=[tournament_id],
        lazy="selectin"
    )
    group: Mapped[Optional["TournamentGroupModel"]] = relationship(
        back_populates="participants",
        foreign_keys=[group_id],
        lazy="selectin"
    )
    student: Mapped["StudentModel"] = relationship(
        back_populates="tournament_participations",
        foreign_keys=[student_id],
        lazy="selectin"
    )


class TournamentMatchModel(ModelMixin):
    """
    比赛对阵模型
    """
    __tablename__: str = 'badminton_tournament_match'
    __table_args__: dict[str, str] = ({'comment': '比赛对阵表'})
    __loader_options__: list[str] = ["tournament", "group", "player1", "player2", "winner"]

    tournament_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('badminton_tournament.id', ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
        comment="赛事ID"
    )
    group_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey('badminton_tournament_group.id', ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        index=True,
        comment="分组ID"
    )
    
    # 对阵信息
    round_number: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment="轮次")
    match_number: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment="场次")
    player1_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('badminton_tournament_participant.id', ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="选手1ID"
    )
    player2_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('badminton_tournament_participant.id', ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="选手2ID"
    )
    
    # 比赛状态
    status: Mapped[MatchStatusEnum] = mapped_column(
        Enum(MatchStatusEnum),
        default=MatchStatusEnum.SCHEDULED,
        nullable=False,
        comment="比赛状态"
    )
    scheduled_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="计划时间")
    actual_start_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="实际开始时间")
    actual_end_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="实际结束时间")
    
    # 比分信息（JSON格式存储详细比分）
    # 格式: {"sets": [{"player1": 21, "player2": 19}, ...], "winner": "player1"}
    scores: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="比分详情")
    winner_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey('badminton_tournament_participant.id', ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        comment="获胜者ID"
    )
    
    # 关联关系
    tournament: Mapped["TournamentModel"] = relationship(
        back_populates="matches",
        foreign_keys=[tournament_id],
        lazy="selectin"
    )
    group: Mapped[Optional["TournamentGroupModel"]] = relationship(
        back_populates="matches",
        foreign_keys=[group_id],
        lazy="selectin"
    )
    player1: Mapped["TournamentParticipantModel"] = relationship(
        foreign_keys=[player1_id],
        lazy="selectin"
    )
    player2: Mapped["TournamentParticipantModel"] = relationship(
        foreign_keys=[player2_id],
        lazy="selectin"
    )
    winner: Mapped[Optional["TournamentParticipantModel"]] = relationship(
        foreign_keys=[winner_id],
        lazy="selectin"
    )