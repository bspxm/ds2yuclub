from __future__ import annotations

from datetime import date, time
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, Enum, ForeignKey, Integer, SmallInteger, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import ModelMixin, UserMixin
from ..enums import CourseTypeEnum

if TYPE_CHECKING:
    from app.api.v1.module_system.user.model import UserModel
    from ..student.model import StudentModel
    from ..leave.model import LeaveRequestModel


class CourseModel(ModelMixin, UserMixin):
    """
    课程模型
    """
    __tablename__: str = 'badminton_course'
    __table_args__: dict[str, str] = ({'comment': '课程表'})
    __loader_options__: list[str] = ["coach_user", "enrollments", "created_by", "updated_by"]

    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="课程名称")
    course_type: Mapped[CourseTypeEnum] = mapped_column(
        Enum(CourseTypeEnum, values_callable=lambda x: [e.value for e in x]),
        default=CourseTypeEnum.REGULAR,
        nullable=False,
        comment="课程类型"
    )
    
    # 教练信息
    coach_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey('sys_user.id', ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        comment="教练ID"
    )
    coach_name: Mapped[str | None] = mapped_column(String(32), nullable=True, comment="教练姓名")
    
    # 时间安排
    start_date: Mapped[date] = mapped_column(Date, nullable=False, comment="开始日期")
    end_date: Mapped[date] = mapped_column(Date, nullable=False, comment="结束日期")
    class_time: Mapped[time] = mapped_column(Time, nullable=False, comment="上课时间")
    duration_minutes: Mapped[int] = mapped_column(SmallInteger, default=60, nullable=False, comment="课程时长(分钟)")
    day_of_week: Mapped[str | None] = mapped_column(String(10), nullable=True, comment="星期几（如周一）")
    
    # 课程容量
    max_students: Mapped[int] = mapped_column(SmallInteger, default=10, nullable=False, comment="最大学生数")
    min_students: Mapped[int] = mapped_column(SmallInteger, default=2, nullable=False, comment="最少学生数")
    current_enrollment: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False, comment="当前报名人数")
    
    # 课程信息
    location: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="上课地点")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="课程描述")
    requirements: Mapped[str | None] = mapped_column(Text, nullable=True, comment="课程要求")
    
    # 状态
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False, comment="课程状态")
    
    # 关联关系
    coach_user: Mapped[Optional["UserModel"]] = relationship(
        foreign_keys=[coach_id],
        lazy="selectin"
    )
    enrollments: Mapped[list["StudentCourseModel"]] = relationship(
        back_populates="course",
        lazy="selectin",
        cascade="all, delete-orphan"
    )


class StudentCourseModel(ModelMixin):
    """
    学员报班模型
    """
    __tablename__: str = 'badminton_student_course'
    __table_args__: dict[str, str] = ({'comment': '学员报班表'})
    __loader_options__: list[str] = ["student", "course", "leave_records"]

    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('badminton_student.id', ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
        comment="学员ID"
    )
    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('badminton_course.id', ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
        comment="课程ID"
    )
    
    # 报名信息
    enrollment_date: Mapped[date] = mapped_column(Date, nullable=False, comment="报名日期")
    enrollment_status: Mapped[str] = mapped_column(String(20), default="active", nullable=False, comment="报名状态")
    enrollment_notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="报名备注")
    
    # 统计信息
    total_classes: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False, comment="总课程数")
    attended_classes: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False, comment="已上课数")
    missed_classes: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False, comment="缺勤次数")
    leave_classes: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False, comment="请假次数")
    
    # 关联关系
    student: Mapped["StudentModel"] = relationship(
        back_populates="course_enrollments",
        foreign_keys=[student_id],
        lazy="selectin"
    )
    course: Mapped["CourseModel"] = relationship(
        back_populates="enrollments",
        foreign_keys=[course_id],
        lazy="selectin"
    )
    leave_records: Mapped[list["LeaveRequestModel"]] = relationship(
        back_populates="student_course",
        lazy="selectin",
        cascade="all, delete-orphan"
    )