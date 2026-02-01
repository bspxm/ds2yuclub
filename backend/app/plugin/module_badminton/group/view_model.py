from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.dialects.postgresql import JSONB

from app.utils.common_util import uuid4_str

if TYPE_CHECKING:
    pass


class MappedBase(AsyncAttrs, DeclarativeBase):
    """声明式基类（用于视图模型）"""
    __abstract__: bool = True


class ModelMixinForView(MappedBase):
    """
    视图模型混入类
    """
    __abstract__: bool = True

    # 基础字段
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='主键ID', index=True)
    uuid: Mapped[str] = mapped_column(String(64), default=uuid4_str, nullable=False, unique=True, comment='UUID全局唯一标识', index=True)
    description: Mapped[str | None] = mapped_column(Text, default=None, nullable=True, comment="备注/描述")
    created_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment='创建时间')
    updated_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment='更新时间')
    created_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='创建人ID')
    updated_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='更新人ID')


class GroupListView(ModelMixinForView):
    """
    分组列表视图模型
    用于优化查询性能，避免 ORM 预加载在远程数据库上的性能问题
    """
    __tablename__: str = 'view_badminton_group_list'
    __table_args__: dict[str, str] = ({'comment': '分组列表视图'})
    __loader_options__: list[str] = []  # 视图不需要预加载

    # 分组基本信息
    name: Mapped[str] = mapped_column(String(64), nullable=False, comment='分组名称')
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment='备注说明')

    # 统计字段
    coach_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment='教练数量')
    student_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment='学员数量')

    # JSON 聚合字段（教练和学员列表）
    coaches_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=[], comment='教练列表JSON')
    students_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=[], comment='学员列表JSON')