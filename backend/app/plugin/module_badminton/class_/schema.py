"""
class_模块 - Schema定义
"""

from datetime import date, datetime, time
from typing import Optional

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator, model_serializer

from app.api.v1.module_system.user.schema import UserOutSchema
from app.core.base_schema import BaseSchema, UserBySchema
from app.core.validator import DateStr, DateTimeStr, TimeStr

from ..enums import (
    ClassTypeEnum,
    ClassStatusEnum,
    AttendanceStatusEnum,
    ScheduleStatusEnum,
    ScheduleTypeEnum
)

class ClassCreateSchema(BaseModel):
    """班级创建模型"""
    semester_id: int = Field(..., description='学期ID')
    name: str = Field(..., description='班级名称')
    class_type: ClassTypeEnum = Field(default=ClassTypeEnum.FIXED, description='班级类型')
    coach_id: int = Field(..., description='教练ID')
    total_sessions: int = Field(..., description='总课时数')
    session_duration: int = Field(default=90, description='单次课时长(分钟)')
    session_price: float = Field(..., description='课时单价')
    max_students: int = Field(default=10, description='最大学员数')
    min_students: int = Field(default=1, description='最小学员数')
    start_date: Optional[DateStr] = Field(None, description='开始日期')
    end_date: Optional[DateStr] = Field(None, description='结束日期')
    is_active: bool = Field(default=True, description='是否激活')
    enrollment_open: bool = Field(default=True, description='是否开放报名')
    description: Optional[str] = Field(None, description='班级描述')
    notes: Optional[str] = Field(None, description='备注')

class ClassUpdateSchema(ClassCreateSchema):
    """班级更新模型"""
    semester_id: Optional[int] = Field(None, description='学期ID')
    name: Optional[str] = Field(None, description='班级名称')
    class_type: Optional[ClassTypeEnum] = Field(None, description='班级类型')
    coach_id: Optional[int] = Field(None, description='教练ID')
    total_sessions: Optional[int] = Field(None, description='总课时数')
    session_price: Optional[float] = Field(None, description='课时单价')

class ClassOutSchema(ClassCreateSchema, BaseSchema, UserBySchema):
    """班级响应模型"""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

class ClassAttendanceCreateSchema(BaseModel):
    """班级考勤创建模型"""
    student_id: int = Field(..., description='学员ID')
    class_id: int = Field(..., description='班级ID')
    schedule_id: Optional[int] = Field(None, description='排课记录ID')
    purchase_id: int = Field(..., description='购买记录ID')
    attendance_date: DateStr = Field(..., description='考勤日期')
    start_time: TimeStr = Field(..., description='开始时间')
    end_time: TimeStr = Field(..., description='结束时间')
    duration_minutes: int = Field(..., description='课时分钟数')
    attendance_status: AttendanceStatusEnum = Field(default=AttendanceStatusEnum.PRESENT, description='考勤状态')
    is_leave: bool = Field(default=False, description='是否请假')
    leave_reason: Optional[str] = Field(None, description='请假原因')
    is_makeup: bool = Field(default=False, description='是否补课')
    makeup_date: Optional[DateStr] = Field(None, description='补课日期')
    makeup_notes: Optional[str] = Field(None, description='补课备注')
    coach_id: int = Field(..., description='确认教练ID')
    confirmed_by_coach: bool = Field(default=False, description='教练是否确认')

class ClassAttendanceUpdateSchema(ClassAttendanceCreateSchema):
    """班级考勤更新模型"""
    student_id: Optional[int] = Field(None, description='学员ID')
    class_id: Optional[int] = Field(None, description='班级ID')
    purchase_id: Optional[int] = Field(None, description='购买记录ID')
    attendance_date: Optional[DateStr] = Field(None, description='考勤日期')
    start_time: Optional[TimeStr] = Field(None, description='开始时间')
    end_time: Optional[TimeStr] = Field(None, description='结束时间')
    attendance_status: Optional[AttendanceStatusEnum] = Field(None, description='考勤状态')

class ClassAttendanceOutSchema(ClassAttendanceCreateSchema, BaseSchema, UserBySchema):
    """班级考勤响应模型"""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

class ClassScheduleCreateSchema(BaseModel):
    """班级排课创建模型"""
    class_id: int = Field(..., description='班级ID')
    schedule_date: DateStr = Field(..., description='排课日期')
    start_time: TimeStr = Field(..., description='开始时间')
    end_time: TimeStr = Field(..., description='结束时间')
    duration_minutes: int = Field(..., description='课时分钟数')
    schedule_status: ScheduleStatusEnum = Field(default=ScheduleStatusEnum.SCHEDULED, description='排课状态')
    schedule_type: ScheduleTypeEnum = Field(default=ScheduleTypeEnum.REGULAR, description='排课类型')
    coach_id: int = Field(..., description='教练ID')
    court_number: Optional[str] = Field(None, description='场地号')
    max_attendance: Optional[int] = Field(None, description='最大考勤人数')
    notes: Optional[str] = Field(None, description='备注')

class ClassScheduleUpdateSchema(ClassScheduleCreateSchema):
    """班级排课更新模型"""
    class_id: Optional[int] = Field(None, description='班级ID')
    schedule_date: Optional[DateStr] = Field(None, description='排课日期')
    start_time: Optional[TimeStr] = Field(None, description='开始时间')
    end_time: Optional[TimeStr] = Field(None, description='结束时间')
    schedule_status: Optional[ScheduleStatusEnum] = Field(None, description='排课状态')
    schedule_type: Optional[ScheduleTypeEnum] = Field(None, description='排课类型')
    coach_id: Optional[int] = Field(None, description='教练ID')

class ClassScheduleOutSchema(ClassScheduleCreateSchema, BaseSchema, UserBySchema):
    """班级排课响应模型"""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class ClassQueryParam:
    """班级查询参数"""
    def __init__(
        self,
        name: Optional[str] = Query(None, description="班级名称"),
        class_type: Optional[ClassTypeEnum] = Query(None, description="班级类型"),
        semester_id: Optional[int] = Query(None, description="学期ID"),
        status: Optional[ClassStatusEnum] = Query(None, description="班级状态"),
        coach_id: Optional[int] = Query(None, description="教练ID"),
        created_time: Optional[list[DateTimeStr]] = Query(None, description="创建时间范围"),
        updated_time: Optional[list[DateTimeStr]] = Query(None, description="更新时间范围")
    ) -> None:
        # 模糊查询字段
        if name:
            self.name = ("like", f"%{name}%")
        
        # 精确查询字段
        if class_type:
            self.class_type = ("eq", class_type)
        if semester_id is not None and not hasattr(semester_id, 'field_info'):
            self.semester_id = ("eq", semester_id)
        if status:
            self.status = ("eq", status)
        if coach_id is not None and not hasattr(coach_id, 'field_info'):
            self.coach_id = ("eq", coach_id)
        
        # 时间范围查询
        if created_time and isinstance(created_time, list) and len(created_time) == 2:
            self.created_time = ("between", (created_time[0], created_time[1]))
        if updated_time and isinstance(updated_time, list) and len(updated_time) == 2:
            self.updated_time = ("between", (updated_time[0], updated_time[1]))
        
        # 确保不包含created_id和updated_id查询条件
        if hasattr(self, 'created_id'):
            delattr(self, 'created_id')
        if hasattr(self, 'updated_id'):
            delattr(self, 'updated_id')


class ClassAttendanceQueryParam:
    """考勤记录查询参数"""
    def __init__(
        self,
        student_id: Optional[int] = Query(None, description="学员ID"),
        class_id: Optional[int] = Query(None, description="班级ID"),
        schedule_id: Optional[int] = Query(None, description="排课记录ID"),
        attendance_status: Optional[AttendanceStatusEnum] = Query(None, description="考勤状态"),
        attendance_date_start: Optional[str] = Query(None, description="考勤日期范围-起始"),
        attendance_date_end: Optional[str] = Query(None, description="考勤日期范围-结束"),
        created_time: Optional[list[DateTimeStr]] = Query(None, description="创建时间范围"),
        updated_time: Optional[list[DateTimeStr]] = Query(None, description="更新时间范围")
    ) -> None:
        # 精确查询字段
        if student_id is not None and not hasattr(student_id, 'field_info'):
            self.student_id = ("eq", student_id)
        if class_id is not None and not hasattr(class_id, 'field_info'):
            self.class_id = ("eq", class_id)
        if schedule_id is not None and not hasattr(schedule_id, 'field_info'):
            self.schedule_id = ("eq", schedule_id)
        if attendance_status:
            self.attendance_status = ("eq", attendance_status)
        
        # 日期范围查询
        if attendance_date_start and attendance_date_end:
            self.attendance_date = ("between", (attendance_date_start, attendance_date_end))
        elif attendance_date_start:
            self.attendance_date = ("ge", attendance_date_start)
        elif attendance_date_end:
            self.attendance_date = ("le", attendance_date_end)
        
        # 时间范围查询
        if created_time and isinstance(created_time, list) and len(created_time) == 2:
            self.created_time = ("between", (created_time[0], created_time[1]))
        if updated_time and isinstance(updated_time, list) and len(updated_time) == 2:
            self.updated_time = ("between", (updated_time[0], updated_time[1]))
        
        # 确保不包含created_id和updated_id查询条件
        if hasattr(self, 'created_id'):
            delattr(self, 'created_id')
        if hasattr(self, 'updated_id'):
            delattr(self, 'updated_id')


class ClassScheduleQueryParam:
    """排课记录查询参数"""
    def __init__(
        self,
        class_id: Optional[int] = Query(None, description="班级ID"),
        schedule_date_start: Optional[str] = Query(None, description="排课日期范围-起始"),
        schedule_date_end: Optional[str] = Query(None, description="排课日期范围-结束"),
        schedule_status: Optional[ScheduleStatusEnum] = Query(None, description="排课状态"),
        created_time: Optional[list[DateTimeStr]] = Query(None, description="创建时间范围"),
        updated_time: Optional[list[DateTimeStr]] = Query(None, description="更新时间范围")
    ) -> None:
        # 精确查询字段
        if class_id is not None and not hasattr(class_id, 'field_info'):
            self.class_id = ("eq", class_id)
        if schedule_status:
            self.schedule_status = ("eq", schedule_status)
        
        # 日期范围查询
        if schedule_date_start and schedule_date_end:
            self.schedule_date = ("between", (schedule_date_start, schedule_date_end))
        elif schedule_date_start:
            self.schedule_date = ("ge", schedule_date_start)
        elif schedule_date_end:
            self.schedule_date = ("le", schedule_date_end)
        
        # 时间范围查询
        if created_time and isinstance(created_time, list) and len(created_time) == 2:
            self.created_time = ("between", (created_time[0], created_time[1]))
        if updated_time and isinstance(updated_time, list) and len(updated_time) == 2:
            self.updated_time = ("between", (updated_time[0], updated_time[1]))
        
        # 确保不包含created_id和updated_id查询条件
        if hasattr(self, 'created_id'):
            delattr(self, 'created_id')
        if hasattr(self, 'updated_id'):
            delattr(self, 'updated_id')
