from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, Enum, Float, ForeignKey, Integer, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from app.core.base_model import ModelMixin, UserMixin
from ..enums import GenderEnum, HandednessEnum, RelationTypeEnum

if TYPE_CHECKING:
    from app.api.v1.module_system.user.model import UserModel
    from ..tournament.model import TournamentParticipantModel
    from ..course.model import StudentCourseModel
    from ..purchase.model import PurchaseModel
    from ..attendance.model import ClassAttendanceModel


class StudentModel(ModelMixin, UserMixin):
    """
    学员模型
    """
    __tablename__: str = 'badminton_student'
    __table_args__: dict[str, str] = ({'comment': '学员表'})
    __loader_options__: list[str] = ["created_by", "updated_by"]

    # 基本信息
    name: Mapped[str] = mapped_column(String(32), nullable=False, comment='姓名')
    english_name: Mapped[str | None] = mapped_column(String(64), nullable=True, comment='英文名')
    gender: Mapped[GenderEnum] = mapped_column(Enum(GenderEnum), default=GenderEnum.UNKNOWN, nullable=False, comment='性别')
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment='出生日期')
    height: Mapped[float | None] = mapped_column(Float, nullable=True, comment='身高(cm)')
    weight: Mapped[float | None] = mapped_column(Float, nullable=True, comment='体重(kg)')
    handedness: Mapped[HandednessEnum] = mapped_column(Enum(HandednessEnum), default=HandednessEnum.RIGHT, nullable=False, comment='惯用手')
    
    # 训练信息
    join_date: Mapped[date] = mapped_column(Date, nullable=False, comment='入训日期')
    level: Mapped[str | None] = mapped_column(String(32), nullable=True, comment='技术水平等级')
    group_name: Mapped[str | None] = mapped_column(String(64), nullable=True, comment='所属组别')
    campus: Mapped[str | None] = mapped_column(String(128), nullable=True, comment='所属校区')
    
    # 联系方式（备用）
    emergency_contact: Mapped[str | None] = mapped_column(String(32), nullable=True, comment='紧急联系人')
    emergency_phone: Mapped[str | None] = mapped_column(String(20), nullable=True, comment='紧急联系电话')
    
    # 统计信息
    total_matches: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment='总比赛场次')
    wins: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment='胜场数')
    losses: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment='负场数')
    win_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False, comment='胜率')
    
    # 关联关系
    parents: Mapped[list["UserModel"]] = relationship(
        secondary="badminton_parent_student",
        lazy="selectin",
        back_populates="students"
    )
    assessments: Mapped[list["AbilityAssessmentModel"]] = relationship(
        back_populates="student",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    tournament_participations: Mapped[list["TournamentParticipantModel"]] = relationship(
        back_populates="student",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    course_enrollments: Mapped[list["StudentCourseModel"]] = relationship(
        back_populates="student",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    purchases: Mapped[list["PurchaseModel"]] = relationship(
        back_populates="student",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    attendance_records: Mapped[list["ClassAttendanceModel"]] = relationship(
        back_populates="student",
        lazy="selectin",
        cascade="all, delete-orphan"
    )


class ParentStudentModel(ModelMixin):
    """
    家长-学员关联模型
    """
    __tablename__: str = "badminton_parent_student"
    __table_args__: dict[str, str] = ({'comment': '家长-学员关联表'})

    parent_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sys_user.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        comment="家长用户ID"
    )
    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("badminton_student.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        comment="学员ID"
    )
    relation_type: Mapped[RelationTypeEnum] = mapped_column(
        Enum(RelationTypeEnum),
        default=RelationTypeEnum.OTHER,
        nullable=False,
        comment="关系类型"
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否为主要联系人")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")

    # 关联关系
    parent: Mapped["UserModel"] = relationship(
        foreign_keys=[parent_id],
        lazy="selectin",
        overlaps="parents"
    )
    student: Mapped["StudentModel"] = relationship(
        foreign_keys=[student_id],
        lazy="selectin",
        overlaps="parents"
    )


class AbilityAssessmentModel(ModelMixin, UserMixin):
    """
    能力评估历史模型
    """
    __tablename__: str = 'badminton_ability_assessment'
    __table_args__: dict[str, str] = ({'comment': '能力评估历史表'})
    __loader_options__: list[str] = ["student", "created_by", "updated_by"]

    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('badminton_student.id', ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
        comment="学员ID"
    )
    assessment_date: Mapped[date] = mapped_column(Date, nullable=False, comment="评估日期")
    coach_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey('sys_user.id', ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        comment="评估教练ID"
    )
    
    # 9项能力评分（1-5分）
    technique: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment="手法(1-5)")
    footwork: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment="步法(1-5)")
    tactics: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment="战术(1-5)")
    power: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment="力量(1-5)")
    speed: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment="速度(1-5)")
    stamina: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment="体能(1-5)")
    offense: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment="进攻(1-5)")
    defense: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment="防守(1-5)")
    mental: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment="心理(1-5)")
    
    # 综合评分
    overall_score: Mapped[float] = mapped_column(Float, nullable=False, comment="综合评分")
    comments: Mapped[str | None] = mapped_column(Text, nullable=True, comment="教练评语")
    
    # 关联关系
    student: Mapped["StudentModel"] = relationship(
        back_populates="assessments",
        foreign_keys=[student_id],
        lazy="selectin"
    )
    coach: Mapped[Optional["UserModel"]] = relationship(
        foreign_keys=[coach_id],
        lazy="selectin"
    )