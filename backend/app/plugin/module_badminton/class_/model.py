from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, Enum, Float, ForeignKey, Integer, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import ModelMixin, UserMixin
from ..enums import ClassTypeEnum

if TYPE_CHECKING:
    from app.api.v1.module_system.user.model import UserModel
    from ..semester.model import SemesterModel
    from ..schedule.model import ClassScheduleModel
    from ..purchase.model import PurchaseModel


class ClassModel(ModelMixin, UserMixin):
    """
    班级模型
    """
    __tablename__: str = 'badminton_class'
    __table_args__: dict[str, str] = ({'comment': '班级表'})
    __loader_options__: list[str] = ["semester", "coach_user", "created_by", "updated_by"]

    # 基本信息
    semester_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('badminton_semester.id', ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment='学期ID'
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment='班级名称')
    class_type: Mapped[ClassTypeEnum] = mapped_column(
        Enum(ClassTypeEnum),
        nullable=False,
        comment='班级类型'
    )
    
    # 教练信息
    coach_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('sys_user.id', ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment='教练ID'
    )
    
    # 课时配置
    total_sessions: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment='总课时数')
    session_duration: Mapped[int] = mapped_column(SmallInteger, default=90, comment='单次课时长(分钟)')
    session_price: Mapped[float] = mapped_column(Float, nullable=False, comment='课时单价')
    
    # 班级容量
    max_students: Mapped[int] = mapped_column(SmallInteger, default=10, comment='最大学员数')
    min_students: Mapped[int] = mapped_column(SmallInteger, default=1, comment='最小学员数')
    current_students: Mapped[int] = mapped_column(SmallInteger, default=0, comment='当前学员数')
    
    # 时间安排（对于固定天班级）
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment='开始日期')
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment='结束日期')
    
    # 状态信息
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment='是否激活')
    enrollment_open: Mapped[bool] = mapped_column(Boolean, default=True, comment='是否开放报名')
    
    # 描述信息
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment='班级描述')
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment='备注')
    
    # 关联关系
    semester: Mapped["SemesterModel"] = relationship(
        back_populates="classes",
        foreign_keys=[semester_id],
        lazy="selectin"
    )
    coach_user: Mapped["UserModel"] = relationship(
        foreign_keys=[coach_id],
        lazy="selectin"
    )
    schedules: Mapped[list["ClassScheduleModel"]] = relationship(
        back_populates="class_ref",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    purchases: Mapped[list["PurchaseModel"]] = relationship(
        back_populates="class_ref",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    attendance_records: Mapped[list["ClassAttendanceModel"]] = relationship(
        back_populates="class_ref",
        lazy="selectin",
        cascade="all, delete-orphan"
    )