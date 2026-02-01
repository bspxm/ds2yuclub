from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, Enum, Float, Integer, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.dialects.postgresql import JSONB

from app.utils.common_util import uuid4_str
from ..enums import GenderEnum, HandednessEnum

if TYPE_CHECKING:
    pass


class MappedBase(AsyncAttrs, DeclarativeBase):
    """声明式基类（用于视图模型）"""
    __abstract__: bool = True


class ModelMixinForView(MappedBase):
    """
    视图模型混入类 - 包含 status 和 status_flag 字段
    """
    __abstract__: bool = True

    # 基础字段
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='主键ID', index=True)
    uuid: Mapped[str] = mapped_column(String(64), default=uuid4_str, nullable=False, unique=True, comment='UUID全局唯一标识', index=True)
    description: Mapped[str | None] = mapped_column(Text, default=None, nullable=True, comment="备注/描述")
    status: Mapped[str] = mapped_column(String(10), default='0', nullable=False, comment="状态(0:正常 1:停用)", index=True)
    created_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment='创建时间')
    updated_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment='更新时间')
    created_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='创建人ID')
    updated_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='更新人ID')


class StudentListView(ModelMixinForView):
    """
    学员列表视图模型
    用于优化查询性能，避免 ORM 预加载在远程数据库上的性能问题
    """
    __tablename__: str = 'view_badminton_student_list'
    __table_args__: dict[str, str] = ({'comment': '学员列表视图'})
    __loader_options__: list[str] = []  # 视图不需要预加载

    # 基本信息
    name: Mapped[str] = mapped_column(String(32), nullable=False, comment='姓名')
    english_name: Mapped[str | None] = mapped_column(String(64), nullable=True, comment='英文名')
    gender: Mapped[GenderEnum] = mapped_column(Enum(GenderEnum, values_callable=lambda x: [e.value for e in x]), default=GenderEnum.UNKNOWN, nullable=False, comment='性别')
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment='出生日期')
    height: Mapped[float | None] = mapped_column(Float, nullable=True, comment='身高(cm)')
    weight: Mapped[float | None] = mapped_column(Float, nullable=True, comment='体重(kg)')
    handedness: Mapped[HandednessEnum] = mapped_column(Enum(HandednessEnum, values_callable=lambda x: [e.value for e in x]), default=HandednessEnum.RIGHT, nullable=False, comment='惯用手')

    # 训练信息
    join_date: Mapped[date] = mapped_column(Date, nullable=False, comment='入训日期')
    level: Mapped[str | None] = mapped_column(String(32), nullable=True, comment='技术水平等级')
    group_name: Mapped[str | None] = mapped_column(String(64), nullable=True, comment='所属组别')
    campus: Mapped[str | None] = mapped_column(String(128), nullable=True, comment='所属校区')

    # 联系方式
    contact: Mapped[str | None] = mapped_column(String(32), nullable=True, comment='联系人')
    mobile: Mapped[str | None] = mapped_column(String(20), nullable=True, comment='手机号码')

    # 统计信息
    total_matches: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment='总比赛场次')
    wins: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment='胜场数')
    losses: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment='负场数')
    win_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False, comment='胜率')

    # 家长统计和JSON聚合字段
    parent_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment='家长数量')
    parents_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=[], comment='家长列表JSON')