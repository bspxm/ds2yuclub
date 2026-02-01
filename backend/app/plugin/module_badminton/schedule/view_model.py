from __future__ import annotations

from datetime import date, datetime, time
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, Integer, SmallInteger, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin

if TYPE_CHECKING:
    pass


class ClassScheduleListView(ModelMixin):
    """
    排课记录列表视图模型
    用于优化查询性能，避免 ORM 预加载在远程数据库上的性能问题
    """
    __tablename__: str = 'view_badminton_class_schedule_list'
    __table_args__: dict[str, str] = ({'comment': '排课记录列表视图'})
    __loader_options__: list[str] = []  # 视图不需要预加载，所有数据已包含

    # 排课记录字段
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='ID')
    uuid: Mapped[str] = mapped_column(String(32), nullable=False, comment='UUID')
    class_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='班级ID')
    schedule_date: Mapped[date] = mapped_column(Date, nullable=False, comment='排课日期')
    day_of_week: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment='星期几（0-6，0=周日）')
    time_slot_code: Mapped[str | None] = mapped_column(String(32), nullable=True, comment='时间段代码（A-E）')
    time_slots_json: Mapped[str | None] = mapped_column(Text, nullable=True, comment='时间段JSON配置')
    start_time: Mapped[time | None] = mapped_column(Time, nullable=True, comment='开始时间')
    end_time: Mapped[time | None] = mapped_column(Time, nullable=True, comment='结束时间')
    duration_minutes: Mapped[int | None] = mapped_column(SmallInteger, nullable=True, comment='课时分钟数')
    schedule_type: Mapped[str] = mapped_column(String(32), nullable=False, comment='排课类型')
    schedule_status: Mapped[str] = mapped_column(String(32), nullable=False, comment='排课状态')
    coach_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='教练ID')
    coach_confirmed: Mapped[bool] = mapped_column(Boolean, default=False, comment='教练是否确认')
    coach_confirm_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment='教练确认时间')
    court_number: Mapped[str | None] = mapped_column(String(32), nullable=True, comment='场地号')
    location: Mapped[str | None] = mapped_column(String(128), nullable=True, comment='具体位置')
    topic: Mapped[str | None] = mapped_column(String(256), nullable=True, comment='课程主题')
    content_summary: Mapped[str | None] = mapped_column(Text, nullable=True, comment='内容摘要')
    training_focus: Mapped[str | None] = mapped_column(String(256), nullable=True, comment='训练重点')
    equipment_needed: Mapped[str | None] = mapped_column(Text, nullable=True, comment='所需器材')
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, comment='是否已发布给家长')
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment='发布时间')
    is_auto_generated: Mapped[bool] = mapped_column(Boolean, default=False, comment='是否自动生成')
    original_schedule_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='原始排课ID（用于补课）')
    makeup_for_schedule_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='补课对应排课ID')
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment='备注')
    status: Mapped[str] = mapped_column(String(32), nullable=False, comment='状态')
    created_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment='创建时间')
    updated_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment='更新时间')
    created_id: Mapped[int] = mapped_column(Integer, nullable=True, comment='创建人ID')
    updated_id: Mapped[int] = mapped_column(Integer, nullable=True, comment='更新人ID')

    # 班级信息（视图字段）
    class_ref_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='班级ID（视图字段）')
    class_ref_name: Mapped[str | None] = mapped_column(String(128), nullable=True, comment='班级名称（视图字段）')
    class_ref_semester_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='学期ID（视图字段）')

    # 教练信息（视图字段）
    coach_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='教练ID（视图字段）')
    coach_user_name: Mapped[str | None] = mapped_column(String(128), nullable=True, comment='教练名称（视图字段）')