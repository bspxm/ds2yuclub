import enum


class GenderEnum(enum.Enum):
    """性别枚举"""
    MALE = "0"      # 男
    FEMALE = "1"    # 女
    UNKNOWN = "2"   # 未知


class HandednessEnum(enum.Enum):
    """惯用手枚举"""
    RIGHT = "right"      # 右手
    LEFT = "left"        # 左手
    BOTH = "both"        # 双手


class RelationTypeEnum(enum.Enum):
    """家长-学员关系类型枚举"""
    FATHER = "father"        # 父亲
    MOTHER = "mother"        # 母亲
    GRANDFATHER = "grandfather"  # 祖父
    GRANDMOTHER = "grandmother"  # 祖母
    GUARDIAN = "guardian"    # 监护人
    OTHER = "other"          # 其他


class TournamentTypeEnum(enum.Enum):
    """赛事类型枚举（对应4种赛制）"""
    ROUND_ROBIN = "round_robin"            # 分组循环赛（带淘汰赛）
    PURE_GROUP = "pure_group"              # 纯小组赛
    PROMOTION_RELEGATION = "promotion_relegation"  # 定区升降赛
    SINGLE_ELIMINATION = "single_elimination"      # 小组单败制淘汰赛


class TournamentStatusEnum(enum.Enum):
    """赛事状态枚举"""
    DRAFT = "draft"          # 草稿
    REGISTRATION = "registration"  # 报名中
    IN_PROGRESS = "in_progress"    # 进行中
    COMPLETED = "completed"        # 已结束
    CANCELLED = "cancelled"        # 已取消


class MatchStatusEnum(enum.Enum):
    """比赛状态枚举"""
    SCHEDULED = "scheduled"        # 已安排
    IN_PROGRESS = "in_progress"    # 进行中
    COMPLETED = "completed"        # 已完成
    CANCELLED = "cancelled"        # 已取消
    WALKOVER = "walkover"          # 弃权


class CourseTypeEnum(enum.Enum):
    """课程类型枚举"""
    REGULAR = "regular"        # 常规课
    PRIVATE = "private"        # 私教课
    GROUP = "group"            # 小组课
    COMPETITION = "competition"  # 比赛课
    THEORY = "theory"          # 理论课


class LeaveStatusEnum(enum.Enum):
    """请假状态枚举"""
    PENDING = "pending"        # 待审核
    APPROVED = "approved"      # 已批准
    REJECTED = "rejected"      # 已拒绝
    CANCELLED = "cancelled"    # 已取消


class SemesterTypeEnum(enum.Enum):
    """学期类型枚举"""
    REGULAR = "regular"        # 常规学期（春秋）
    SUMMER = "summer"          # 暑假学期
    WINTER = "winter"          # 寒假学期


class ClassTypeEnum(enum.Enum):
    """班级类型枚举"""
    FIXED = "fixed"            # 固定天训练（每周固定时间）
    FLEXIBLE = "flexible"      # 自选天训练（家长选择时间）


class PurchaseTypeEnum(enum.Enum):
    """购买类型枚举"""
    NEW = "new"              # 新购
    RENEWAL = "renewal"      # 续费
    CARRYOVER = "carryover"  # 结转
    UPGRADE = "upgrade"      # 升级

class PurchaseStatusEnum(enum.Enum):
    """购买记录状态枚举"""
    ACTIVE = "active"          # 活跃中（课时未用完）
    COMPLETED = "completed"    # 已完成（课时已用完）
    EXPIRED = "expired"        # 已过期（超过有效期）
    SETTLED = "settled"        # 已结算（学期结束已结算）
    CANCELLED = "cancelled"    # 已取消


class AttendanceStatusEnum(enum.Enum):
    """考勤状态枚举"""
    PRESENT = "present"        # 出席（正常上课）
    ABSENT = "absent"          # 缺勤（未请假未上课）
    LEAVE = "leave"            # 请假（已批准请假）
    MAKEUP = "makeup"          # 补课（请假后补课）
    CANCELLED = "cancelled"    # 取消（课程取消）


class SemesterStatusEnum(enum.Enum):
    """学期状态枚举"""
    PLANNING = "planning"      # 规划中
    ACTIVE = "active"          # 进行中
    COMPLETED = "completed"    # 已结束
    SETTLED = "settled"        # 已结算
    ARCHIVED = "archived"      # 已归档


class ScheduleStatusEnum(enum.Enum):
    """排课状态枚举"""
    SCHEDULED = "scheduled"        # 已安排
    CONFIRMED = "confirmed"        # 已确认
    IN_PROGRESS = "in_progress"    # 进行中
    COMPLETED = "completed"        # 已完成
    CANCELLED = "cancelled"        # 已取消
    MAKEUP = "makeup"              # 补课


class ScheduleTypeEnum(enum.Enum):
    """排课类型枚举"""
    REGULAR = "regular"            # 常规课
    MAKEUP = "makeup"              # 补课
    EXTRA = "extra"                # 加课
    CANCELLED = "cancelled"        # 取消课（占位）


class ClassStatusEnum(enum.Enum):
    """班级状态枚举"""
    ACTIVE = "active"              # 激活中
    INACTIVE = "inactive"          # 未激活
    FULL = "full"                  # 已满员
    CLOSED = "closed"              # 已关闭
    ARCHIVED = "archived"          # 已归档