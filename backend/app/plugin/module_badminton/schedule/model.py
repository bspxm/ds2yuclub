from __future__ import annotations

import enum
from datetime import date, datetime, time
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, SmallInteger, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import ModelMixin, UserMixin
from ..enums import ScheduleStatusEnum, ScheduleTypeEnum

if TYPE_CHECKING:
    from app.api.v1.module_system.user.model import UserModel
    from ..class_.model import ClassModel
    from ..attendance.model import ClassAttendanceModel


# ============================================================================
# 排课模型定义
# ============================================================================

class ClassScheduleModel(ModelMixin, UserMixin):
    """
    班级排课模型
    """
    __tablename__: str = 'badminton_class_schedule'
    __table_args__: dict[str, str] = ({'comment': '班级排课表'})
    __loader_options__: list[str] = ["class_ref", "coach_user", "attendance_records", "created_by", "updated_by"]

    # 关联信息
    class_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('badminton_class.id', ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment='班级ID'
    )
    
    # 时间信息
    schedule_date: Mapped[date] = mapped_column(Date, nullable=False, comment='排课日期')
    day_of_week: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment='星期几（0-6，0=周日）')
    time_slot_id: Mapped[int | None] = mapped_column(SmallInteger, nullable=True, comment='时间段ID（保留用于兼容）')
    time_slot_code: Mapped[str | None] = mapped_column(String(32), nullable=True, comment='时间段代码（A-E）')
    time_slots_json: Mapped[str | None] = mapped_column(Text, nullable=True, comment='时间段JSON配置（星期+代码格式）')
    start_time: Mapped[time | None] = mapped_column(Time, nullable=True, comment='开始时间')
    end_time: Mapped[time | None] = mapped_column(Time, nullable=True, comment='结束时间')
    duration_minutes: Mapped[int | None] = mapped_column(SmallInteger, nullable=True, comment='课时分钟数')
    
    # 排课信息
    schedule_type: Mapped[ScheduleTypeEnum] = mapped_column(
        Enum(ScheduleTypeEnum, values_callable=lambda x: [e.value for e in x]),
        default=ScheduleTypeEnum.REGULAR,
        nullable=False,
        comment='排课类型'
    )
    schedule_status: Mapped[ScheduleStatusEnum] = mapped_column(
        Enum(ScheduleStatusEnum, values_callable=lambda x: [e.value for e in x]),
        default=ScheduleStatusEnum.SCHEDULED,
        nullable=False,
        comment='排课状态'
    )
    
    # 教练信息
    coach_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('sys_user.id', ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment='教练ID'
    )
    coach_confirmed: Mapped[bool] = mapped_column(Boolean, default=False, comment='教练是否确认')
    coach_confirm_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment='教练确认时间')
    
    # 场地信息
    court_number: Mapped[str | None] = mapped_column(String(32), nullable=True, comment='场地号')
    location: Mapped[str | None] = mapped_column(String(128), nullable=True, comment='具体位置')
    
    # 课程内容
    topic: Mapped[str | None] = mapped_column(String(256), nullable=True, comment='课程主题')
    content_summary: Mapped[str | None] = mapped_column(Text, nullable=True, comment='内容摘要')
    training_focus: Mapped[str | None] = mapped_column(String(256), nullable=True, comment='训练重点')
    equipment_needed: Mapped[str | None] = mapped_column(Text, nullable=True, comment='所需器材')
    
    # 状态信息
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, comment='是否已发布给家长')
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment='发布时间')
    is_auto_generated: Mapped[bool] = mapped_column(Boolean, default=False, comment='是否自动生成')
    
    # 关联信息
    original_schedule_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey('badminton_class_schedule.id', ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        comment='原始排课ID（用于补课）'
    )
    makeup_for_schedule_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey('badminton_class_schedule.id', ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        comment='补课对应排课ID'
    )
    
    # 描述信息
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment='备注')
    
    # 关联关系
    class_ref: Mapped[Any] = relationship(
        "ClassModel",
        back_populates="schedules",
        foreign_keys=[class_id],
        lazy="selectin"
    )
    coach_user: Mapped["UserModel"] = relationship(
        foreign_keys=[coach_id],
        lazy="selectin"
    )
    original_schedule: Mapped["ClassScheduleModel"] = relationship(
        foreign_keys=[original_schedule_id],
        remote_side="ClassScheduleModel.id",
        lazy="selectin"
    )
    makeup_schedule: Mapped["ClassScheduleModel"] = relationship(
        foreign_keys=[makeup_for_schedule_id],
        lazy="selectin"
    )
    attendance_records: Mapped[list["ClassAttendanceModel"]] = relationship(
        back_populates="schedule",
        lazy="selectin",
        cascade="all, delete-orphan"
    )