from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import ModelMixin, UserMixin

if TYPE_CHECKING:
    from app.api.v1.module_system.user.model import UserModel
    from ..student.model import StudentModel


class AbilityGroupModel(ModelMixin, UserMixin):
    """
    能力分组模型
    """
    __tablename__: str = 'badminton_group'
    __table_args__: dict[str, str] = ({'comment': '能力分组表'})
    __loader_options__: list[str] = ["created_by", "updated_by"]

    name: Mapped[str] = mapped_column(String(64), nullable=False, comment='分组名称')
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment='备注说明')

    # 关联关系
    coaches: Mapped[list["UserModel"]] = relationship(
        secondary="badminton_group_coach",
        lazy="selectin",
        back_populates="groups",
        overlaps="coach"
    )
    students: Mapped[list["StudentModel"]] = relationship(
        secondary="badminton_group_student",
        lazy="selectin",
        back_populates="groups",
        overlaps="student"
    )


class GroupCoachModel(ModelMixin):
    """
    分组-教练关联模型
    """
    __tablename__: str = "badminton_group_coach"
    __table_args__: dict[str, str] = ({'comment': '分组-教练关联表'})

    group_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("badminton_group.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        comment="分组ID"
    )
    coach_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sys_user.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        comment="教练用户ID"
    )

    # 关联关系
    group: Mapped["AbilityGroupModel"] = relationship(
        foreign_keys=[group_id],
        lazy="selectin",
        overlaps="coaches"
    )
    coach: Mapped["UserModel"] = relationship(
        foreign_keys=[coach_id],
        lazy="selectin",
        overlaps="groups"
    )


class GroupStudentModel(ModelMixin):
    """
    分组-学员关联模型
    """
    __tablename__: str = "badminton_group_student"
    __table_args__: dict[str, str] = ({'comment': '分组-学员关联表'})

    group_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("badminton_group.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        comment="分组ID"
    )
    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("badminton_student.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        comment="学员ID"
    )

    # 关联关系
    group: Mapped["AbilityGroupModel"] = relationship(
        foreign_keys=[group_id],
        lazy="selectin",
        overlaps="students"
    )
    student: Mapped["StudentModel"] = relationship(
        foreign_keys=[student_id],
        lazy="selectin",
        overlaps="groups"
    )