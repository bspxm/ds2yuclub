from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, Enum, Float, Integer, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin
from ..enums import PurchaseStatusEnum

if TYPE_CHECKING:
    pass


class PurchaseListView(ModelMixin):
    """
    购买记录列表视图模型
    用于优化查询性能，避免 ORM 预加载在远程数据库上的性能问题
    """
    __tablename__: str = 'view_badminton_purchase_list'
    __table_args__: dict[str, str] = ({'comment': '购买记录列表视图'})
    __loader_options__: list[str] = []  # 视图不需要预加载，所有数据已包含

    # 购买信息
    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='ID')
    uuid: Mapped[str] = mapped_column(String(64), nullable=False, comment='UUID')
    student_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='学员ID')
    class_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='班级ID')
    semester_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='学期ID')
    purchase_date: Mapped[date] = mapped_column(Date, nullable=False, comment='购买日期')
    
    # 课时信息
    total_sessions: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment='购买总课时')
    used_sessions: Mapped[int] = mapped_column(SmallInteger, default=0, comment='已使用课时')
    remaining_sessions: Mapped[int] = mapped_column(SmallInteger, default=0, comment='剩余课时')
    carry_over_sessions: Mapped[int] = mapped_column(SmallInteger, default=0, comment='结转课时')
    credit_sessions: Mapped[int] = mapped_column(SmallInteger, default=0, comment='信用欠课时')
    
    # 时间限制
    valid_from: Mapped[date] = mapped_column(Date, nullable=False, comment='有效期开始')
    valid_until: Mapped[date] = mapped_column(Date, nullable=False, comment='有效期截止')
    
    # 状态信息
    status: Mapped[PurchaseStatusEnum] = mapped_column(
        Enum(PurchaseStatusEnum, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        comment='购买状态'
    )
    is_settled: Mapped[bool] = mapped_column(Boolean, default=False, comment='是否已结算')
    settlement_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment='结算日期')
    
    # 财务信息
    original_price: Mapped[float] = mapped_column(Float, nullable=False, comment='原价')
    actual_price: Mapped[float] = mapped_column(Float, nullable=False, comment='实付价格')
    discount_rate: Mapped[float] = mapped_column(Float, default=1.0, comment='折扣率')
    
    # 描述信息
    purchase_notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment='购买备注')
    selected_time_slots: Mapped[str | None] = mapped_column(Text, nullable=True, comment='已选上课时间段ID列表（JSON格式）')
    
    # 基础字段
    description: Mapped[str | None] = mapped_column(Text, default=None, nullable=True, comment="备注/描述")
    created_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment='创建时间')
    updated_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment='更新时间')
    created_id: Mapped[int] = mapped_column(Integer, nullable=True, comment='创建人ID')
    updated_id: Mapped[int] = mapped_column(Integer, nullable=True, comment='更新人ID')

    # 学员信息（视图字段）
    student_ref_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='学员ID（视图字段）')
    student_name: Mapped[str | None] = mapped_column(String(32), nullable=True, comment='学员姓名（视图字段）')
    student_gender: Mapped[str | None] = mapped_column(String(16), nullable=True, comment='学员性别（视图字段）')
    student_mobile: Mapped[str | None] = mapped_column(String(20), nullable=True, comment='学员手机号（视图字段）')

    # 班级信息（视图字段）
    class_ref_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='班级ID（视图字段）')
    class_name: Mapped[str | None] = mapped_column(String(128), nullable=True, comment='班级名称（视图字段）')
    class_type: Mapped[str | None] = mapped_column(String(32), nullable=True, comment='班级类型（视图字段）')
    class_coach_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='班级教练ID（视图字段）')

    # 学期信息（视图字段）
    semester_ref_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='学期ID（视图字段）')
    semester_name: Mapped[str | None] = mapped_column(String(64), nullable=True, comment='学期名称（视图字段）')
    semester_type: Mapped[str | None] = mapped_column(String(32), nullable=True, comment='学期类型（视图字段）')

    # 教练信息（视图字段）
    coach_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='教练ID（视图字段）')
    coach_user_name: Mapped[str | None] = mapped_column(String(64), nullable=True, comment='教练名称（视图字段）')