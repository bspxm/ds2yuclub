"""
羽毛球模块数据模型 - 主入口点

此文件作为向后兼容的桥接文件，重新导出所有按功能拆分的模型。
新的代码应该直接从各个功能模块导入模型，例如：
    from .student import StudentModel
    from .semester import SemesterModel
    from .class import ClassModel
"""

# ============================================================================
# 枚举类型（从enums.py重新导出）
# ============================================================================

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
    SemesterStatusEnum
)

# ============================================================================
# 学员相关模型
# ============================================================================

from .student import (
    StudentModel,
    ParentStudentModel,
    AbilityAssessmentModel
)

# ============================================================================
# 赛事相关模型
# ============================================================================

from .tournament import (
    TournamentModel,
    TournamentGroupModel,
    TournamentParticipantModel,
    TournamentMatchModel
)

# ============================================================================
# 课程相关模型（旧系统）
# ============================================================================

from .course import (
    CourseModel,
    StudentCourseModel
)

# ============================================================================
# 请假相关模型
# ============================================================================

from .leave import (
    LeaveRequestModel
)

# ============================================================================
# 学期制课时结算系统模型
# ============================================================================

from .semester import SemesterModel
from .class_ import ClassModel
from .purchase import PurchaseModel
from .attendance import ClassAttendanceModel
from .schedule import ClassScheduleModel, ScheduleStatusEnum, ScheduleTypeEnum

# ============================================================================
# 所有导出的符号
# ============================================================================

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

# 注意：UserModel 关联关系已在 app/api/v1/module_system/user/model.py 中扩展