from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import ModelMixin
from ..enums import LeaveStatusEnum

if TYPE_CHECKING:
    from app.api.v1.module_system.user.model import UserModel
    from ..course.model import StudentCourseModel


class LeaveRequestModel(ModelMixin):
    """
    请假记录模型
    """
    __tablename__: str = 'badminton_leave_record'
    __table_args__: dict[str, str] = ({'comment': '请假记录表'})
    __loader_options__: list[str] = ["student_course", "processed_by"]

    student_course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('badminton_student_course.id', ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
        comment="学员报班ID"
    )
    
    # 请假信息
    leave_date: Mapped[date] = mapped_column(Date, nullable=False, comment="请假日期")
    leave_reason: Mapped[str] = mapped_column(String(255), nullable=False, comment="请假原因")
    leave_status: Mapped[LeaveStatusEnum] = mapped_column(
        Enum(LeaveStatusEnum, values_callable=lambda x: [e.value for e in x]),
        default=LeaveStatusEnum.PENDING,
        nullable=False,
        comment="请假状态"
    )
    
    # 处理信息
    processed_by_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey('sys_user.id', ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        comment="处理人ID"
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="处理时间")
    process_notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="处理备注")
    
    # 关联关系
    student_course: Mapped["StudentCourseModel"] = relationship(
        back_populates="leave_records",
        foreign_keys=[student_course_id],
        lazy="selectin"
    )
    processed_by: Mapped[Optional["UserModel"]] = relationship(
        foreign_keys=[processed_by_id],
        lazy="selectin"
    )