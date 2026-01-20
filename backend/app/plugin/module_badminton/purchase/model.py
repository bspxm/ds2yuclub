from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, Date, Enum, Float, ForeignKey, Integer, SmallInteger, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import ModelMixin, UserMixin
from ..enums import PurchaseStatusEnum

if TYPE_CHECKING:
    from ..student.model import StudentModel
    from ..class_.model import ClassModel
    from ..semester.model import SemesterModel
    from ..attendance.model import ClassAttendanceModel


class PurchaseModel(ModelMixin, UserMixin):
    """
    购买记录模型
    """
    __tablename__: str = 'badminton_purchase'
    __table_args__: dict[str, str] = ({'comment': '购买记录表'})
    __loader_options__: list[str] = ["student", "class_ref", "semester", "created_by", "updated_by"]

    # 购买信息
    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('badminton_student.id', ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment='学员ID'
    )
    class_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('badminton_class.id', ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment='班级ID'
    )
    semester_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('badminton_semester.id', ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment='学期ID'
    )
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
        Enum(PurchaseStatusEnum),
        default=PurchaseStatusEnum.ACTIVE,
        nullable=False,
        comment='购买状态'
    )
    is_settled: Mapped[bool] = mapped_column(Boolean, default=False, comment='是否已结算')
    settlement_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment='结算日期')
    
    # 财务信息（记录用，不涉及实际资金流）
    original_price: Mapped[float] = mapped_column(Float, nullable=False, comment='原价')
    actual_price: Mapped[float] = mapped_column(Float, nullable=False, comment='实付价格')
    discount_rate: Mapped[float] = mapped_column(Float, default=1.0, comment='折扣率')
    
    # 描述信息
    purchase_notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment='购买备注')
    
    # 关联关系
    student: Mapped[Any] = relationship(
        "StudentModel",
        back_populates="purchases",
        foreign_keys=[student_id],
        lazy="selectin"
    )
    class_ref: Mapped[Any] = relationship(
        "ClassModel",
        back_populates="purchases",
        foreign_keys=[class_id],
        lazy="selectin"
    )
    semester: Mapped[Any] = relationship(
        "SemesterModel",
        back_populates="purchases",
        foreign_keys=[semester_id],
        lazy="selectin"
    )
    attendance_records: Mapped[list["ClassAttendanceModel"]] = relationship(
        back_populates="purchase",
        lazy="selectin",
        cascade="all, delete-orphan"
    )