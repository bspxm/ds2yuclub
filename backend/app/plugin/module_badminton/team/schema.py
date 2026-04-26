"""
class_模块 - Schema定义
"""

from datetime import date, datetime, time
from typing import Optional, Any

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator, model_serializer, field_serializer, BeforeValidator

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

# ============================================================================
# 辅助函数
# ============================================================================

def enum_to_str(value: Any) -> str:
    """将枚举值转换为字符串"""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return value.value if hasattr(value, 'value') else str(value)

class ClassCreateSchema(BaseModel):
    """班级创建模型"""
    semester_id: int = Field(..., description='学期ID')
    name: str = Field(..., description='班级名称')
    class_type: ClassTypeEnum = Field(default=ClassTypeEnum.FIXED, description='班级类型')
    coach_id: Optional[int] = Field(None, description='教练ID')
    total_sessions: int = Field(..., description='总课时数')
    sessions_per_week: Optional[int] = Field(None, description='每周课次')
    session_duration: Optional[int] = Field(90, description='单次课时长(分钟)')
    session_price: Optional[float] = Field(None, description='课时单价')
    max_students: int = Field(default=10, description='最大学员数')
    min_students: int = Field(default=1, description='最小学员数')
    start_date: Optional[DateStr] = Field(None, description='开始日期')
    end_date: Optional[DateStr] = Field(None, description='结束日期')
    weekly_schedule: Optional[str] = Field(None, description='每周排班(如：周一、周三、周五)')
    time_slots_json: Optional[str] = Field(None, description='时间段JSON配置')
    location: Optional[str] = Field(None, description='上课地点')
    class_status: ClassStatusEnum = Field(default=ClassStatusEnum.PENDING, description='班级状态')
    is_active: bool = Field(default=True, description='是否激活')
    enrollment_open: bool = Field(default=True, description='是否开放报名')
    fee_per_session: Optional[float] = Field(None, description='每节课费用')
    description: Optional[str] = Field(None, description='班级描述')
    notes: Optional[str] = Field(None, description='备注')

class ClassUpdateSchema(ClassCreateSchema):
    """班级更新模型"""
    semester_id: Optional[int] = Field(None, description='学期ID')
    name: Optional[str] = Field(None, description='班级名称')
    class_type: Optional[ClassTypeEnum] = Field(None, description='班级类型')
    coach_id: Optional[int] = Field(None, description='教练ID')
    class_status: Optional[ClassStatusEnum] = Field(None, description='班级状态')
    total_sessions: Optional[int] = Field(None, description='总课时数')
    session_price: Optional[float] = Field(None, description='课时单价')

# 关联对象的简单Schema定义
class SemesterSimpleSchema(BaseModel):
    """学期简单信息"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str

class UserSimpleSchema(BaseModel):
    """用户简单信息"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str

class ClassSimpleSchema(BaseModel):
    """班级简单信息"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    semester_id: int

class ClassOutSchema(ClassCreateSchema, BaseSchema, UserBySchema):
    """班级响应模型"""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    
    # 关联对象
    semester: Optional[SemesterSimpleSchema] = Field(None, description='学期信息')
    coach_user: Optional[UserSimpleSchema] = Field(None, description='教练信息')

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
    session_deducted: int = Field(default=1, description='扣除课时数')
    is_auto_deduct: bool = Field(default=True, description='是否自动扣课时')

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

class ClassScheduleCreateV2Schema(BaseModel):
    """班级排课创建模型（V2版本）- 支持学员选择和自动创建考勤"""
    semester_id: int = Field(..., description='学期ID')
    schedule_date: DateStr = Field(..., description='排课日期')
    class_ids: list[int] = Field(..., description='班级ID列表（支持多选）')
    coach_id: int = Field(..., description='教练ID')
    time_slots: dict[str, list[str]] = Field(..., description='时间段配置（星期+代码格式，如：{"周一": ["A", "B"], "周三": ["C"]}）')
    schedule_status: str = Field(default='scheduled', description='排课状态')
    schedule_type: str = Field(default='regular', description='排课类型')
    student_ids: list[int] = Field(..., description='学员ID列表')
    location: Optional[str] = Field(None, description='具体位置')
    topic: Optional[str] = Field(None, description='课程主题')
    content_summary: Optional[str] = Field(None, description='内容摘要')
    training_focus: Optional[str] = Field(None, description='训练重点')
    equipment_needed: Optional[str] = Field(None, description='所需器材')
    notes: Optional[str] = Field(None, description='备注')

    # 配置模型以接受枚举输入
    model_config = ConfigDict(from_attributes=True)


class AvailableStudentSchema(BaseModel):
    """可用学员信息模型"""
    student_id: int = Field(..., description='学员ID', alias='id')
    uuid: str = Field(..., description='学员UUID')
    name: str = Field(..., description='学员姓名')
    student_name: str = Field(..., description='学员姓名（别名，用于前端显示）')
    english_name: Optional[str] = Field(None, description='英文名')
    gender: Optional[str] = Field(None, description='性别')
    birth_date: Optional[DateStr] = Field(None, description='出生日期')
    level: Optional[str] = Field(None, description='技术水平等级')
    group_name: Optional[str] = Field(None, description='所属组别')
    total_sessions: int = Field(..., description='总课时数')
    used_sessions: int = Field(..., description='已使用课时数')
    remaining_sessions: int = Field(..., description='剩余课时数')
    purchase_id: int = Field(..., description='购买记录ID')
    valid_from: DateStr = Field(..., description='有效期开始日期')
    valid_until: DateStr = Field(..., description='有效期结束日期')
    
    # 配置模型
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TimeSlotSchema(BaseModel):
    """时间段信息模型"""
    id: int = Field(..., description='时间段ID')
    code: str = Field(..., description='时间段代码（A-E）')
    time_range: str = Field(..., description='时间段范围（如：08:00-09:30）')
    duration_minutes: int = Field(..., description='时长（分钟）')
    
    # 配置模型
    model_config = ConfigDict(from_attributes=True)

class ClassScheduleOutSchema(BaseSchema, UserBySchema):
    """班级排课响应模型"""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    # 基本信息
    class_id: int = Field(..., description='班级ID')
    semester_id: Optional[int] = Field(None, description='学期ID')
    schedule_date: DateStr = Field(..., description='排课日期')
    day_of_week: int = Field(..., description='星期几（0-6，0=周日）')
    
    # 时间信息
    time_slot_code: Optional[str] = Field(None, description='时间段代码（A-E）')
    time_slots_json: Optional[str] = Field(None, description='时间段JSON配置（星期+代码格式）')
    start_time: Optional[TimeStr] = Field(None, description='开始时间')
    end_time: Optional[TimeStr] = Field(None, description='结束时间')
    duration_minutes: Optional[int] = Field(None, description='课时分钟数')
    
    # 排课信息
    schedule_status: str = Field(..., description='排课状态')
    schedule_type: str = Field(..., description='排课类型')
    
    # 教练信息
    coach_id: int = Field(..., description='教练ID')
    coach_confirmed: bool = Field(default=False, description='教练是否确认')
    coach_confirm_at: Optional[DateTimeStr] = Field(None, description='教练确认时间')
    
    # 场地信息
    court_number: Optional[str] = Field(None, description='场地号')
    location: Optional[str] = Field(None, description='具体位置')
    
    # 课程内容
    topic: Optional[str] = Field(None, description='课程主题')
    content_summary: Optional[str] = Field(None, description='内容摘要')
    training_focus: Optional[str] = Field(None, description='训练重点')
    equipment_needed: Optional[str] = Field(None, description='所需器材')
    
    # 状态信息
    is_published: bool = Field(default=False, description='是否已发布给家长')
    published_at: Optional[DateTimeStr] = Field(None, description='发布时间')
    is_auto_generated: bool = Field(default=False, description='是否自动生成')
    
    # 关联信息
    original_schedule_id: Optional[int] = Field(None, description='原始排课ID（用于补课）')
    makeup_for_schedule_id: Optional[int] = Field(None, description='补课对应排课ID')
    
    # 描述信息
    notes: Optional[str] = Field(None, description='备注')
    
    # 关联对象
    class_: Optional[ClassSimpleSchema] = Field(None, alias='class', description='班级信息')
    
    # 添加学员统计字段
    student_count: Optional[int] = Field(None, description='学员人数')
    attendance_count: Optional[int] = Field(None, description='出勤人数')
    absent_count: Optional[int] = Field(None, description='缺勤人数')
    leave_count: Optional[int] = Field(None, description='请假人数')


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


class AvailableStudentsRequestSchema(BaseModel):
    """获取可用学员请求模型"""
    semester_id: int = Field(..., description='学期ID')
    schedule_date: date = Field(..., description='排课日期')
    time_slots: dict[str, list[str]] = Field(..., description='时间段配置（格式：{"周一": ["A", "B"]}）')
    class_ids: Optional[list[int]] = Field(None, description='班级ID列表（可选）')

    model_config = ConfigDict(from_attributes=True)
