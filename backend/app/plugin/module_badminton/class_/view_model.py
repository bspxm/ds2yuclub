from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, Float, Integer, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

from app.utils.common_util import uuid4_str

if TYPE_CHECKING:
    pass


class MappedBase(AsyncAttrs, DeclarativeBase):
    """声明式基类（用于视图模型）"""
    __abstract__: bool = True


class ModelMixinForView(MappedBase):
    """
    视图模型混入类 - 不包含 status 字段
    """
    __abstract__: bool = True

    # 基础字段（不包含 status）
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='主键ID', index=True)
    uuid: Mapped[str] = mapped_column(String(64), default=uuid4_str, nullable=False, unique=True, comment='UUID全局唯一标识', index=True)
    description: Mapped[str | None] = mapped_column(Text, default=None, nullable=True, comment="备注/描述")
    created_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False, comment='创建时间', index=True)
    updated_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment='更新时间', index=True)


class ClassListView(ModelMixinForView):
    """
    班级列表视图模型
    用于优化查询性能，避免 ORM 预加载在远程数据库上的性能问题
    """
    __tablename__: str = 'view_badminton_class_list'
    __table_args__: dict[str, str] = ({'comment': '班级列表视图'})
    __loader_options__: list[str] = []  # 视图不需要预加载，所有数据已包含

    # 班级字段
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='ID')
    uuid: Mapped[str] = mapped_column(String(64), nullable=False, comment='UUID')
    semester_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='学期ID')
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment='班级名称')
    class_type: Mapped[str] = mapped_column(String(32), nullable=False, comment='班级类型')
    coach_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='教练ID')
    total_sessions: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment='总课时数')
    sessions_per_week: Mapped[int | None] = mapped_column(SmallInteger, nullable=True, comment='每周课次')
    session_duration: Mapped[int] = mapped_column(SmallInteger, default=90, comment='单次课时长(分钟)')
    session_price: Mapped[float | None] = mapped_column(Float, nullable=True, comment='课时单价')
    max_students: Mapped[int] = mapped_column(SmallInteger, default=10, comment='最大学员数')
    min_students: Mapped[int] = mapped_column(SmallInteger, default=1, comment='最小学员数')
    current_students: Mapped[int] = mapped_column(SmallInteger, default=0, comment='当前学员数')
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment='开始日期')
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment='结束日期')
    weekly_schedule: Mapped[str | None] = mapped_column(String(256), nullable=True, comment='每周排班')
    time_slots_json: Mapped[str | None] = mapped_column(Text, nullable=True, comment='时间段JSON配置')
    location: Mapped[str | None] = mapped_column(String(128), nullable=True, comment='上课地点')
    class_status: Mapped[str] = mapped_column(String(32), nullable=False, comment='班级状态')
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment='是否激活')
    enrollment_open: Mapped[bool] = mapped_column(Boolean, default=True, comment='是否开放报名')
    fee_per_session: Mapped[float | None] = mapped_column(Float, nullable=True, comment='每节课费用')
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment='备注')
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment='班级描述')
    created_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment='创建时间')
    updated_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment='更新时间')
    created_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='创建人ID')
    updated_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='更新人ID')

    # 学期信息（视图字段）
    semester_ref_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='学期ID（视图字段）')
    semester_name: Mapped[str | None] = mapped_column(String(64), nullable=True, comment='学期名称（视图字段）')
    semester_type: Mapped[str | None] = mapped_column(String(32), nullable=True, comment='学期类型（视图字段）')

    # 教练信息（视图字段）
    coach_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='教练ID（视图字段）')
    coach_user_name: Mapped[str | None] = mapped_column(String(128), nullable=True, comment='教练名称（视图字段）')