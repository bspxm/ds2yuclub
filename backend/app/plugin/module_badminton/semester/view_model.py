from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, Enum, Integer, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

from app.utils.common_util import uuid4_str
from ..enums import SemesterTypeEnum, SemesterStatusEnum

if TYPE_CHECKING:
    pass


class MappedBase(AsyncAttrs, DeclarativeBase):
    """声明式基类（用于视图模型）"""
    __abstract__: bool = True


class ModelMixinForView(MappedBase):
    """
    视图模型混入类 - 包含 status_flag 字段（学期模型使用）
    """
    __abstract__: bool = True

    # 基础字段
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='主键ID', index=True)
    uuid: Mapped[str] = mapped_column(String(64), default=uuid4_str, nullable=False, unique=True, comment='UUID全局唯一标识', index=True)
    description: Mapped[str | None] = mapped_column(Text, default=None, nullable=True, comment="备注/描述")
    created_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False, comment='创建时间', index=True)
    updated_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment='更新时间', index=True)
    created_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='创建人ID')
    updated_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='更新人ID')


class SemesterListView(ModelMixinForView):
    """
    学期列表视图模型
    用于优化查询性能，避免 ORM 预加载在远程数据库上的性能问题
    """
    __tablename__: str = 'view_badminton_semester_list'
    __table_args__: dict[str, str] = ({'comment': '学期列表视图'})
    __loader_options__: list[str] = []  # 视图不需要预加载

    # 学期基本信息
    name: Mapped[str] = mapped_column(String(64), nullable=False, comment='学期名称')
    semester_type: Mapped[SemesterTypeEnum] = mapped_column(
        Enum(SemesterTypeEnum, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        comment='学期类型'
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False, comment='开始日期')
    end_date: Mapped[date] = mapped_column(Date, nullable=False, comment='结束日期')
    week_count: Mapped[int] = mapped_column(SmallInteger, default=0, comment='总周数')

    # 学期状态
    status: Mapped[SemesterStatusEnum] = mapped_column(
        Enum(SemesterStatusEnum, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        comment='学期状态'
    )
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, comment='是否当前学期')

    # 结算信息
    settlement_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment='结算日期')
    carry_over_enabled: Mapped[bool] = mapped_column(Boolean, default=True, comment='允许课时结转')
    max_carry_over_sessions: Mapped[int] = mapped_column(SmallInteger, default=5, comment='最大结转课时数')

    # 描述信息
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment='学期描述')

    # 学期模型的特殊字段
    status_flag: Mapped[str] = mapped_column(String(10), nullable=False, comment="是否启用(0:启用 1:禁用)", index=True)

    # 统计字段（预留）
    class_count: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='班级数量')
    purchase_count: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='购买记录数量')