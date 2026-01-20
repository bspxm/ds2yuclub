"""
羽毛球培训会员管理系统 - Schema定义主入口

重新导出所有模块的Schema类，保持向后兼容性
"""

from datetime import date, datetime, time
from typing import Optional

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator, model_serializer

from app.api.v1.module_system.user.schema import UserOutSchema
from app.core.base_schema import BaseSchema, UserBySchema
from app.core.validator import DateStr, DateTimeStr, TimeStr
from .response import SimpleResponse

from .model import (
    GenderEnum,
    HandednessEnum,
    RelationTypeEnum,
    TournamentTypeEnum,
    TournamentStatusEnum,
    MatchStatusEnum,
    CourseTypeEnum,
    LeaveStatusEnum,
    SemesterTypeEnum,
    SemesterStatusEnum,
    ClassTypeEnum,
    PurchaseStatusEnum,
    AttendanceStatusEnum,
    ScheduleStatusEnum,
    ScheduleTypeEnum
)

# 重新导出所有模块的Schema类
from .student.schema import (
    StudentCreateSchema,
    StudentUpdateSchema,
    StudentOutSchema,
    StudentQueryParam,
    ParentStudentCreateSchema,
    ParentStudentUpdateSchema,
    ParentStudentOutSchema,
    AbilityAssessmentCreateSchema,
    AbilityAssessmentUpdateSchema,
    AbilityAssessmentOutSchema,
    AbilityAssessmentQueryParam
)

from .tournament.schema import (
    TournamentCreateSchema,
    TournamentUpdateSchema,
    TournamentOutSchema
)

from .course.schema import (
    CourseCreateSchema
)

from .leave.schema import (
    LeaveRequestCreateSchema
)

from .semester.schema import (
    SemesterCreateSchema,
    SemesterUpdateSchema,
    SemesterOutSchema,
    SemesterQueryParam
)

from .class_.schema import (
    ClassCreateSchema,
    ClassUpdateSchema,
    ClassOutSchema,
    ClassQueryParam
)

from .purchase.schema import (
    PurchaseCreateSchema,
    PurchaseUpdateSchema,
    PurchaseOutSchema,
    PurchaseQueryParam
)

from .class_.schema import (
    ClassAttendanceCreateSchema,
    ClassAttendanceUpdateSchema,
    ClassAttendanceOutSchema,
    ClassAttendanceQueryParam
)

from .class_.schema import (
    ClassScheduleCreateSchema,
    ClassScheduleUpdateSchema,
    ClassScheduleOutSchema,
    ClassScheduleQueryParam
)


# ============================================================================
# 通用响应模型
# ============================================================================

class PaginatedResponse(BaseModel):
    """分页响应模型"""
    total: int = Field(..., description="总记录数")
    page_no: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    items: list = Field(..., description="数据列表")


# 导出列表
__all__ = [
    # 通用模型
    'SimpleResponse',
    'PaginatedResponse',
    # 学员相关
    'StudentCreateSchema',
    'StudentUpdateSchema',
    'StudentOutSchema',
    'StudentQueryParam',
    'ParentStudentCreateSchema',
    'ParentStudentUpdateSchema',
    'ParentStudentOutSchema',
    'AbilityAssessmentCreateSchema',
    'AbilityAssessmentUpdateSchema',
    'AbilityAssessmentOutSchema',
    'AbilityAssessmentQueryParam',
    # 赛事相关
    'TournamentCreateSchema',
    'TournamentUpdateSchema',
    'TournamentOutSchema',
    # 课程相关
    'CourseCreateSchema',
    # 请假相关
    'LeaveRequestCreateSchema',
    # 学期相关
    'SemesterCreateSchema',
    'SemesterUpdateSchema',
    'SemesterOutSchema',
    'SemesterQueryParam',
    # 班级相关
    'ClassCreateSchema',
    'ClassUpdateSchema',
    'ClassOutSchema',
    'ClassQueryParam',
    # 购买相关
    'PurchaseCreateSchema',
    'PurchaseUpdateSchema',
    'PurchaseOutSchema',
    'PurchaseQueryParam',
    # 考勤相关
    'ClassAttendanceCreateSchema',
    'ClassAttendanceUpdateSchema',
    'ClassAttendanceOutSchema',
    'ClassAttendanceQueryParam',
    # 排课相关
    'ClassScheduleCreateSchema',
    'ClassScheduleUpdateSchema',
    'ClassScheduleOutSchema',
    'ClassScheduleQueryParam',
]