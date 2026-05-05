from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, Date, Enum, Float, ForeignKey, Integer, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import ModelMixin, UserMixin
from ..enums import ClassTypeEnum, ClassStatusEnum

if TYPE_CHECKING:
    from app.api.v1.module_system.user.model import UserModel
    from ..semester.model import SemesterModel
    from ..schedule.model import ClassScheduleModel
    from ..purchase.model import PurchaseModel
    from ..attendance.model import ClassAttendanceModel


class ClassModel(ModelMixin, UserMixin):
    """
    班级模型
    """
    __tablename__: str = 'badminton_class'
    __table_args__: dict[str, str] = ({'comment': '班级表'})
    __loader_options__: list[str] = []  # 移除预加载以优化远程数据库查询性能

    # 基本信息
    semester_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('badminton_semester.id', ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment='学期ID'
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment='班级名称')
    class_type: Mapped[ClassTypeEnum] = mapped_column(
        Enum(ClassTypeEnum, values_callable=lambda x: [e.value for e in x]),
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
    sessions_per_week: Mapped[int | None] = mapped_column(SmallInteger, nullable=True, comment='每周课次')
    session_duration: Mapped[int] = mapped_column(SmallInteger, default=90, comment='单次课时长(分钟)')
    session_price: Mapped[float | None] = mapped_column(Float, nullable=True, comment='课时单价')
    
    # 班级容量
    max_students: Mapped[int] = mapped_column(SmallInteger, default=10, comment='最大学员数')
    min_students: Mapped[int] = mapped_column(SmallInteger, default=1, comment='最小学员数')
    current_students: Mapped[int] = mapped_column(SmallInteger, default=0, comment='当前学员数')
    
    # 时间安排（对于固定天班级）
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment='开始日期')
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment='结束日期')
    
    # 每周排班信息
    weekly_schedule: Mapped[str | None] = mapped_column(String(256), nullable=True, comment='每周排班(如：周一、周三、周五)')
    time_slots_json: Mapped[str | None] = mapped_column(Text, nullable=True, comment='时间段JSON配置')
    
    # 上课地点
    location: Mapped[str | None] = mapped_column(String(128), nullable=True, comment='上课地点')
    
    # 状态信息
    class_status: Mapped[ClassStatusEnum] = mapped_column(
        Enum(ClassStatusEnum, values_callable=lambda x: [e.value for e in x]),
        default=ClassStatusEnum.ACTIVE,
        nullable=False,
        comment='班级状态'
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment='是否激活')
    enrollment_open: Mapped[bool] = mapped_column(Boolean, default=True, comment='是否开放报名')
    
    # 费用信息（前端使用）
    fee_per_session: Mapped[float | None] = mapped_column(Float, nullable=True, comment='每节课费用')
    
    # 描述信息
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment='班级描述')
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment='备注')
    
    # 关联关系
    semester: Mapped["SemesterModel"] = relationship(
        back_populates="classes",
        foreign_keys=[semester_id],
        lazy="noload"
    )
    coach_user: Mapped["UserModel"] = relationship(
        foreign_keys=[coach_id],
        lazy="noload"
    )
    schedules: Mapped[list[Any]] = relationship(
        "ClassScheduleModel",
        back_populates="class_ref",
        lazy="noload",
        cascade="all, delete-orphan"
    )
    purchases: Mapped[list[Any]] = relationship(
        "PurchaseModel",
        back_populates="class_ref",
        lazy="noload",
        cascade="all, delete-orphan"
    )
    attendance_records: Mapped[list[Any]] = relationship(
        "ClassAttendanceModel",
        back_populates="class_ref",
        lazy="noload",
        cascade="all, delete-orphan"
    )