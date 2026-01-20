"""
羽毛球培训会员管理系统 - Service服务层主入口

重新导出所有模块的Service类，保持向后兼容性
"""

from typing import Any, Optional

import io
import pandas as pd
from datetime import date, datetime

from app.api.v1.module_system.auth.schema import AuthSchema
from app.core.base_schema import BatchSetAvailable
from app.core.exceptions import CustomException
from app.core.logger import log
from app.utils.excel_util import ExcelUtil

# 重新导出所有模块的Service类
from .student.service import StudentService, ParentStudentService, AbilityAssessmentService
from .tournament.service import TournamentService
from .course.service import CourseService
from .leave.service import LeaveRequestService
from .semester.service import SemesterService
from .class_.service import ClassService
from .purchase.service import PurchaseService
from .attendance.service import ClassAttendanceService
from .schedule.service import ClassScheduleService

# 重新导出CRUD类（供Service基类使用）
from .crud import (
    StudentCRUD,
    ParentStudentCRUD,
    AbilityAssessmentCRUD,
    TournamentCRUD,
    CourseCRUD,
    LeaveRequestCRUD,
    SemesterCRUD,
    ClassCRUD,
    PurchaseCRUD,
    ClassAttendanceCRUD,
    ClassScheduleCRUD
)

# 重新导出模型枚举（供Service基类使用）
from .model import GenderEnum, HandednessEnum

# 重新导出Schema类（供Service基类使用）
from .schema import (
    StudentCreateSchema,
    StudentOutSchema,
    StudentQueryParam,
    StudentUpdateSchema,
    ParentStudentCreateSchema,
    ParentStudentOutSchema,
    AbilityAssessmentCreateSchema,
    AbilityAssessmentOutSchema,
    AbilityAssessmentUpdateSchema,
    AbilityAssessmentQueryParam,
    TournamentCreateSchema,
    TournamentOutSchema,
    SimpleResponse,
    PaginatedResponse,
    SemesterCreateSchema,
    SemesterUpdateSchema,
    SemesterOutSchema,
    ClassCreateSchema,
    ClassUpdateSchema,
    ClassOutSchema,
    PurchaseCreateSchema,
    PurchaseUpdateSchema,
    PurchaseOutSchema,
    ClassAttendanceCreateSchema,
    ClassAttendanceUpdateSchema,
    ClassAttendanceOutSchema,
    ClassScheduleCreateSchema,
    ClassScheduleUpdateSchema,
    ClassScheduleOutSchema
)


# ============================================================================
# 基础服务类
# ============================================================================

class BaseBadmintonService:
    """羽毛球模块基础服务类"""
    
    @classmethod
    def get_crud_class(cls, model_name: str) -> type:
        """根据模型名称获取对应的CRUD类"""
        crud_map = {
            'student': StudentCRUD,
            'parent_student': ParentStudentCRUD,
            'ability_assessment': AbilityAssessmentCRUD,
            'tournament': TournamentCRUD,
            'course': CourseCRUD,
            'leave_request': LeaveRequestCRUD,
            'semester': SemesterCRUD,
            'class': ClassCRUD,
            'purchase': PurchaseCRUD,
            'class_attendance': ClassAttendanceCRUD,
            'class_schedule': ClassScheduleCRUD
        }
        
        crud_class = crud_map.get(model_name.lower())
        if not crud_class:
            raise CustomException(msg=f"未找到模型 {model_name} 对应的CRUD类")
        return crud_class


# 导出列表
__all__ = [
    # Service类
    'StudentService',
    'ParentStudentService',
    'AbilityAssessmentService',
    'TournamentService',
    'CourseService',
    'LeaveRequestService',
    'SemesterService',
    'ClassService',
    'PurchaseService',
    'ClassAttendanceService',
    'ClassScheduleService',
    # 基类
    'BaseBadmintonService',
]