"""
羽毛球培训会员管理插件模块

该模块提供羽毛球培训机构的完整会员管理解决方案，包括：
1. 学员管理：学员档案、能力评估、分组管理
2. 比赛管理：支持4种赛制（分组循环赛、纯小组赛、定区升降赛、单败淘汰赛）
3. 课程管理：排课、报班、请假、统计
4. 家长端：学员看板、比赛中心、课程管理
5. 认证扩展：手机号登录、微信登录

模块路由自动注册为：/badminton
"""

__version__ = "1.0.0"

# ============================================================================
# 先导入所有模型，确保 SQLAlchemy 能够正确解析关系
# 注意：导入顺序很重要，有依赖关系的模型需要先导入
# ============================================================================

from .student.model import StudentModel, ParentStudentModel, AbilityAssessmentModel
from .tournament.model import TournamentModel, TournamentGroupModel, TournamentParticipantModel, TournamentMatchModel
from .course.model import CourseModel, StudentCourseModel
from .leave.model import LeaveRequestModel
from .semester.model import SemesterModel
# 先导入schedule模型，因为ClassModel依赖它
from .schedule.model import ClassScheduleModel, ScheduleStatusEnum, ScheduleTypeEnum
from .class_.model import ClassModel
from .purchase.model import PurchaseModel
from .attendance.model import ClassAttendanceModel
from .group.model import AbilityGroupModel, GroupCoachModel, GroupStudentModel

from .enums import (
    GenderEnum,
    HandednessEnum,
    RelationTypeEnum,
    TournamentTypeEnum,
    TournamentStatusEnum,
    MatchStatusEnum,
    CourseTypeEnum,
    LeaveStatusEnum,
    SemesterTypeEnum,
    ClassTypeEnum,
    PurchaseStatusEnum,
    AttendanceStatusEnum,
    SemesterStatusEnum,
)

__all__ = [
    # 枚举类型
    "GenderEnum",
    "HandednessEnum",
    "RelationTypeEnum",
    "TournamentTypeEnum",
    "TournamentStatusEnum",
    "MatchStatusEnum",
    "CourseTypeEnum",
    "LeaveStatusEnum",
    "SemesterTypeEnum",
    "ClassTypeEnum",
    "PurchaseStatusEnum",
    "AttendanceStatusEnum",
    "SemesterStatusEnum",
    "ScheduleStatusEnum",
    "ScheduleTypeEnum",
    
    # 学员相关模型
    "StudentModel",
    "ParentStudentModel",
    "AbilityAssessmentModel",
    
    # 赛事相关模型
    "TournamentModel",
    "TournamentGroupModel",
    "TournamentParticipantModel",
    "TournamentMatchModel",
    
    # 课程相关模型（旧系统）
    "CourseModel",
    "StudentCourseModel",
    
    # 请假相关模型
    "LeaveRequestModel",
    
    # 学期制课时结算系统模型
    "SemesterModel",
    "ClassModel",
    "PurchaseModel",
    "ClassAttendanceModel",
    "ClassScheduleModel",
    
    # 能力分组管理模型
    "AbilityGroupModel",
    "GroupCoachModel",
    "GroupStudentModel",
]

__all__ = [
    # 枚举类型
    "GenderEnum",
    "HandednessEnum",
    "RelationTypeEnum",
    "TournamentTypeEnum",
    "TournamentStatusEnum",
    "MatchStatusEnum",
    "CourseTypeEnum",
    "LeaveStatusEnum",
    "SemesterTypeEnum",
    "ClassTypeEnum",
    "PurchaseStatusEnum",
    "AttendanceStatusEnum",
    "SemesterStatusEnum",
    "ScheduleStatusEnum",
    "ScheduleTypeEnum",
    
    # 学员相关模型
    "StudentModel",
    "ParentStudentModel",
    "AbilityAssessmentModel",
    
    # 赛事相关模型
    "TournamentModel",
    "TournamentGroupModel",
    "TournamentParticipantModel",
    "TournamentMatchModel",
    
    # 课程相关模型（旧系统）
    "CourseModel",
    "StudentCourseModel",
    
    # 请假相关模型
    "LeaveRequestModel",
    
    # 学期制课时结算系统模型
    "SemesterModel",
    "ClassModel",
    "PurchaseModel",
    "ClassAttendanceModel",
    "ClassScheduleModel",
    
    # 能力分组管理模型
    "AbilityGroupModel",
    "GroupCoachModel",
    "GroupStudentModel",
]