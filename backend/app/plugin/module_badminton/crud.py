"""
羽毛球培训会员管理系统 - CRUD数据操作层主入口

重新导出所有模块的CRUD类，保持向后兼容性
"""

from collections.abc import Sequence
from datetime import date, datetime
from typing import Optional

from app.api.v1.module_system.auth.schema import AuthSchema
from app.core.base_crud import CRUDBase

# 重新导出所有模块的CRUD类
from .student.crud import StudentCRUD, ParentStudentCRUD, AbilityAssessmentCRUD
from .tournament.crud import TournamentCRUD, TournamentParticipantCRUD
from .course.crud import CourseCRUD
from .leave.crud import LeaveRequestCRUD
from .semester.crud import SemesterCRUD
from .class_.crud import ClassCRUD
from .purchase.crud import PurchaseCRUD
from .attendance.crud import ClassAttendanceCRUD
from .schedule.crud import ClassScheduleCRUD

# 保持向后兼容的导入（这些模型可能被其他代码直接引用）
from .model import (
    StudentModel,
    ParentStudentModel,
    AbilityAssessmentModel,
    TournamentModel,
    TournamentParticipantModel,
    CourseModel,
    LeaveRequestModel,
    SemesterModel,
    ClassModel,
    PurchaseModel,
    ClassAttendanceModel,
    ClassScheduleModel
)
from .schema import (
    StudentCreateSchema,
    StudentUpdateSchema,
    ParentStudentCreateSchema,
    ParentStudentUpdateSchema,
    AbilityAssessmentCreateSchema,
    AbilityAssessmentUpdateSchema,
    TournamentCreateSchema,
    TournamentUpdateSchema,
    CourseCreateSchema,
    LeaveRequestCreateSchema,
    SemesterCreateSchema,
    SemesterUpdateSchema,
    ClassCreateSchema,
    ClassUpdateSchema,
    PurchaseCreateSchema,
    PurchaseUpdateSchema,
    ClassAttendanceCreateSchema,
    ClassAttendanceUpdateSchema,
    SimpleResponse,
    PaginatedResponse
)

# 导出列表
__all__ = [
    # CRUD类
    'StudentCRUD',
    'ParentStudentCRUD',
    'AbilityAssessmentCRUD',
    'TournamentCRUD',
    'TournamentParticipantCRUD',
    'CourseCRUD',
    'LeaveRequestCRUD',
    'SemesterCRUD',
    'ClassCRUD',
    'PurchaseCRUD',
    'ClassAttendanceCRUD',
    'ClassScheduleCRUD',
    # 模型类
    'StudentModel',
    'ParentStudentModel',
    'AbilityAssessmentModel',
    'TournamentModel',
    'TournamentParticipantModel',
    'CourseModel',
    'LeaveRequestModel',
    'SemesterModel',
    'ClassModel',
    'PurchaseModel',
    'ClassAttendanceModel',
    'ClassScheduleModel',
    # Schema类
    'StudentCreateSchema',
    'StudentUpdateSchema',
    'ParentStudentCreateSchema',
    'ParentStudentUpdateSchema',
    'AbilityAssessmentCreateSchema',
    'AbilityAssessmentUpdateSchema',
    'TournamentCreateSchema',
    'TournamentUpdateSchema',
    'CourseCreateSchema',
    'LeaveRequestCreateSchema',
    'SemesterCreateSchema',
    'SemesterUpdateSchema',
    'ClassCreateSchema',
    'ClassUpdateSchema',
    'PurchaseCreateSchema',
    'PurchaseUpdateSchema',
    'ClassAttendanceCreateSchema',
    'ClassAttendanceUpdateSchema',
    'SimpleResponse',
    'PaginatedResponse',
]