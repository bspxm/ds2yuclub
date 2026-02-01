from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, Date, Enum, ForeignKey, Integer, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import ModelMixin, UserMixin
from ..enums import SemesterTypeEnum, SemesterStatusEnum

if TYPE_CHECKING:
    from ..class_.model import ClassModel
    from ..purchase.model import PurchaseModel


class SemesterModel(ModelMixin, UserMixin):
    """
    学期模型
    """
    __tablename__: str = 'badminton_semester'
    __table_args__: dict[str, str] = ({'comment': '学期表'})
    __loader_options__: list[str] = []  # 移除预加载以优化远程数据库查询性能

    # 覆盖ModelMixin的status字段为status_flag，避免与学期状态字段冲突
    status_flag: Mapped[str] = mapped_column(String(10), default='0', nullable=False, comment="是否启用(0:启用 1:禁用)", index=True)

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
        default=SemesterStatusEnum.PLANNING,
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

    # 关联关系
    classes: Mapped[list[Any]] = relationship(
        "ClassModel",
        back_populates="semester",
        lazy="select",  # 改为惰性加载，避免预加载
        cascade="all, delete-orphan"
    )
    purchases: Mapped[list[Any]] = relationship(
        "PurchaseModel",
        back_populates="semester",
        lazy="select",  # 改为惰性加载，避免预加载
        cascade="all, delete-orphan"
    )