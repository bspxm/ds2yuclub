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
# 数据模型重新导出
# ============================================================================

from .model import (
    # 枚举类型
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
    ScheduleStatusEnum,
    ScheduleTypeEnum,
    
    # 学员相关模型
    StudentModel,
    ParentStudentModel,
    AbilityAssessmentModel,
    
    # 赛事相关模型
    TournamentModel,
    TournamentGroupModel,
    TournamentParticipantModel,
    TournamentMatchModel,
    
    # 课程相关模型（旧系统）
    CourseModel,
    StudentCourseModel,
    
    # 请假相关模型
    LeaveRequestModel,
    
    # 学期制课时结算系统模型
    SemesterModel,
    ClassModel,
    PurchaseModel,
    ClassAttendanceModel,
    ClassScheduleModel,
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
]