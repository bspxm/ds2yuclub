from __future__ import annotations

from datetime import date, datetime, time
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, SmallInteger, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import ModelMixin, UserMixin
from ..enums import AttendanceStatusEnum

if TYPE_CHECKING:
    from app.api.v1.module_system.user.model import UserModel
    from ..student.model import StudentModel
    from ..class_.model import ClassModel
    from ..schedule.model import ClassScheduleModel
    from ..purchase.model import PurchaseModel
    from ..leave.model import LeaveRequestModel


class ClassAttendanceModel(ModelMixin, UserMixin):
    """
    班级考勤模型
    """
    __tablename__: str = 'badminton_class_attendance'
    __table_args__: dict[str, str] = ({'comment': '班级考勤表'})
    __loader_options__: list[str] = ["student", "class_ref", "schedule", "purchase", "created_by", "updated_by"]

    # 关联信息
    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('badminton_student.id', ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment='学员ID'
    )
    class_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('badminton_class.id', ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment='班级ID'
    )
    schedule_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey('badminton_class_schedule.id', ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        comment='排课记录ID'
    )
    purchase_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('badminton_purchase.id', ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment='购买记录ID'
    )
    
    # 时间信息
    attendance_date: Mapped[date] = mapped_column(Date, nullable=False, comment='考勤日期')
    start_time: Mapped[time] = mapped_column(Time, nullable=False, comment='开始时间')
    end_time: Mapped[time] = mapped_column(Time, nullable=False, comment='结束时间')
    duration_minutes: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment='课时分钟数')
    
    # 考勤状态
    attendance_status: Mapped[AttendanceStatusEnum] = mapped_column(
        Enum(AttendanceStatusEnum),
        default=AttendanceStatusEnum.PRESENT,
        nullable=False,
        comment='考勤状态'
    )
    
    # 请假相关
    is_leave: Mapped[bool] = mapped_column(Boolean, default=False, comment='是否请假')
    leave_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey('badminton_leave_record.id', ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        comment='请假记录ID'
    )
    leave_reason: Mapped[str | None] = mapped_column(Text, nullable=True, comment='请假原因')
    
    # 补课相关
    is_makeup: Mapped[bool] = mapped_column(Boolean, default=False, comment='是否补课')
    original_attendance_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey('badminton_class_attendance.id', ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        comment='原考勤记录ID'
    )
    makeup_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment='补课日期')
    makeup_notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment='补课备注')
    
    # 教练确认
    coach_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('sys_user.id', ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment='确认教练ID'
    )
    confirmed_by_coach: Mapped[bool] = mapped_column(Boolean, default=False, comment='教练是否确认')
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment='确认时间')
    
    # 家长确认
    confirmed_by_parent: Mapped[bool] = mapped_column(Boolean, default=False, comment='家长是否确认')
    parent_confirm_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment='家长确认时间')
    
    # 评价信息
    coach_rating: Mapped[int | None] = mapped_column(SmallInteger, nullable=True, comment='教练评分')
    student_rating: Mapped[int | None] = mapped_column(SmallInteger, nullable=True, comment='学员评分')
    parent_rating: Mapped[int | None] = mapped_column(SmallInteger, nullable=True, comment='家长评分')
    coach_comments: Mapped[str | None] = mapped_column(Text, nullable=True, comment='教练评语')
    parent_comments: Mapped[str | None] = mapped_column(Text, nullable=True, comment='家长反馈')
    
    # 课时扣减
    session_deducted: Mapped[int] = mapped_column(SmallInteger, default=1, comment='扣除课时数')
    is_auto_deduct: Mapped[bool] = mapped_column(Boolean, default=True, comment='是否自动扣课时')
    deduction_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment='扣课时日期')
    
    # 关联关系
    student: Mapped["StudentModel"] = relationship(
        back_populates="attendance_records",
        foreign_keys=[student_id],
        lazy="selectin"
    )
    class_ref: Mapped[Any] = relationship(
        "ClassModel",
        back_populates="attendance_records",
        foreign_keys=[class_id],
        lazy="selectin"
    )
    schedule: Mapped[Any] = relationship(
        "ClassScheduleModel",
        back_populates="attendance_records",
        foreign_keys=[schedule_id],
        lazy="selectin"
    )
    purchase: Mapped[Any] = relationship(
        "PurchaseModel",
        back_populates="attendance_records",
        foreign_keys=[purchase_id],
        lazy="selectin"
    )
    coach_user: Mapped["UserModel"] = relationship(
        foreign_keys=[coach_id],
        lazy="selectin"
    )
    leave_record: Mapped["LeaveRequestModel"] = relationship(
        foreign_keys=[leave_id],
        lazy="selectin"
    )
    original_attendance: Mapped["ClassAttendanceModel"] = relationship(
        foreign_keys=[original_attendance_id],
        remote_side="ClassAttendanceModel.id",
        lazy="selectin"
    )
    makeup_attendance: Mapped["ClassAttendanceModel"] = relationship(
        foreign_keys=[original_attendance_id],
        lazy="selectin",
        overlaps="original_attendance"
    )