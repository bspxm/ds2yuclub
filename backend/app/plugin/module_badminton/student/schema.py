"""
student模块 - Schema定义
"""

from datetime import date, datetime, time
from typing import Optional

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator, model_serializer

from app.api.v1.module_system.user.schema import UserOutSchema
from app.core.base_schema import BaseSchema, UserBySchema
from app.core.validator import DateStr, DateTimeStr, TimeStr

from ..enums import (
GenderEnum, HandednessEnum, RelationTypeEnum
)

# ============================================================================
# 学员相关 Schema
# ============================================================================

class StudentCreateSchema(BaseModel):
    """学员创建模型"""
    name: str = Field(..., description='姓名')
    english_name: Optional[str] = Field(None, description='英文名')
    gender: GenderEnum = Field(default=GenderEnum.UNKNOWN, description='性别')
    birth_date: Optional[DateStr] = Field(None, description='出生日期')
    height: Optional[float] = Field(None, description='身高(cm)')
    weight: Optional[float] = Field(None, description='体重(kg)')
    handedness: HandednessEnum = Field(default=HandednessEnum.RIGHT, description='惯用手')
    join_date: DateStr = Field(..., description='入训日期')
    level: Optional[str] = Field(None, description='技术水平等级')
    group_name: Optional[str] = Field(None, description='所属组别')
    campus: Optional[str] = Field(None, description='所属校区')
    emergency_contact: Optional[str] = Field(None, description='紧急联系人')
    emergency_phone: Optional[str] = Field(None, description='紧急联系电话')

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """验证姓名"""
        v = v.strip()
        if not v:
            raise ValueError('姓名不能为空')
        if len(v) < 2 or len(v) > 32:
            raise ValueError('姓名长度必须在2-32个字符之间')
        return v

    @field_validator('emergency_phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """验证电话号码"""
        if v is None:
            return v
        v = v.strip()
        # 简单的手机号验证（11位数字）
        if not v.isdigit() or len(v) != 11:
            raise ValueError('手机号格式不正确（应为11位数字）')
        return v

    @field_validator('birth_date', 'join_date')
    @classmethod
    def validate_date_fields(cls, v: Optional[str | date]) -> Optional[DateStr]:
        """验证日期字段，支持字符串和date对象输入"""
        if v is None:
            return v
        
        # 如果已经是date对象，直接返回
        if isinstance(v, date):
            return v
        
        # 如果是字符串，尝试解析
        if isinstance(v, str):
            v = v.strip()
            if v == "":
                return None
            
            # 尝试常见日期格式
            date_formats = [
                "%Y-%m-%d",      # 2023-01-28
                "%Y/%m/%d",      # 2023/01/28
                "%Y.%m.%d",      # 2023.01.28
                "%Y年%m月%d日",   # 2023年01月28日
                "%d/%m/%Y",      # 28/01/2023 (欧洲格式)
                "%m/%d/%Y",      # 01/28/2023 (美国格式)
            ]
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(v, fmt).date()
                except ValueError:
                    continue
            
            # 尝试使用dateutil.parser（如果可用）
            try:
                from dateutil import parser
                return parser.parse(v).date()
            except ImportError:
                pass
            
            # 最后尝试直接使用datetime.fromisoformat（Python 3.7+）
            try:
                return date.fromisoformat(v)
            except ValueError:
                pass
            
            raise ValueError(f"无法解析日期字符串: {v}，支持的格式: YYYY-MM-DD, YYYY/MM/DD, YYYY.MM.DD等")
        
        raise TypeError(f"不支持的日期类型: {type(v)}")

    @model_validator(mode='after')
    def _after_validation(self):
        """后置验证"""
        # 出生日期不能晚于今天
        if self.birth_date:
            # 将DateStr转换为date对象进行比较
            birth_date_obj = date.fromisoformat(self.birth_date) if isinstance(self.birth_date, str) else self.birth_date
            if birth_date_obj > date.today():
                raise ValueError('出生日期不能晚于今天')
        
        # 入训日期不能晚于今天
        if self.join_date:
            # 将DateStr转换为date对象进行比较
            join_date_obj = date.fromisoformat(self.join_date) if isinstance(self.join_date, str) else self.join_date
            if join_date_obj > date.today():
                raise ValueError('入训日期不能晚于今天')
        
        # 如果提供了身高体重，进行合理性检查
        if self.height is not None and (self.height < 50 or self.height > 250):
            raise ValueError('身高应在50-250cm之间')
        if self.weight is not None and (self.weight < 10 or self.weight > 200):
            raise ValueError('体重应在10-200kg之间')
        
        return self

class StudentUpdateSchema(StudentCreateSchema):
    """学员更新模型"""
    # 更新时所有字段都是可选的
    name: Optional[str] = Field(None, description='姓名')
    join_date: Optional[DateStr] = Field(None, description='入训日期')

class StudentOutSchema(StudentCreateSchema, BaseSchema, UserBySchema):
    """学员响应模型"""
    total_matches: int = Field(0, description='总比赛场次')
    wins: int = Field(0, description='胜场数')
    losses: int = Field(0, description='负场数')
    win_rate: float = Field(0.0, description='胜率')
    
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

class StudentQueryParam:
    """学员查询参数"""
    def __init__(
        self,
        name: Optional[str] = Query(None, description="姓名"),
        gender: Optional[GenderEnum] = Query(None, description="性别"),
        group_name: Optional[str] = Query(None, description="所属组别"),
        campus: Optional[str] = Query(None, description="所属校区"),
        level: Optional[str] = Query(None, description="技术水平等级"),
        min_age: Optional[int] = Query(None, description="最小年龄"),
        max_age: Optional[int] = Query(None, description="最大年龄"),
        created_time: Optional[list[DateTimeStr]] = Query(None, description="创建时间范围"),
        updated_time: Optional[list[DateTimeStr]] = Query(None, description="更新时间范围")
    ) -> None:
        # 模糊查询字段
        if name:
            self.name = ("like", f"%{name}%")
        if group_name:
            self.group_name = ("like", f"%{group_name}%")
        if campus:
            self.campus = ("like", f"%{campus}%")
        if level:
            self.level = ("like", f"%{level}%")
        
        # 精确查询字段
        if gender:
            self.gender = ("eq", gender)
        
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

# ============================================================================
# 家长-学员关联 Schema
# ============================================================================

class ParentStudentCreateSchema(BaseModel):
    """家长-学员关联创建模型"""
    parent_id: int = Field(..., description="家长用户ID")
    student_id: int = Field(..., description="学员ID")
    relation_type: RelationTypeEnum = Field(default=RelationTypeEnum.OTHER, description="关系类型")
    is_primary: bool = Field(default=False, description="是否为主要联系人")
    notes: Optional[str] = Field(None, description="备注")

    @field_validator('parent_id', 'student_id')
    @classmethod
    def validate_ids(cls, v: int) -> int:
        """验证ID"""
        if v <= 0:
            raise ValueError('ID必须大于0')
        return v

class ParentStudentUpdateSchema(ParentStudentCreateSchema):
    """家长-学员关联更新模型"""
    parent_id: Optional[int] = Field(None, description="家长用户ID")
    student_id: Optional[int] = Field(None, description="学员ID")

class ParentStudentOutSchema(ParentStudentCreateSchema, BaseSchema):
    """家长-学员关联响应模型"""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

# ============================================================================
# 能力评估 Schema
# ============================================================================

class AbilityAssessmentCreateSchema(BaseModel):
    """能力评估创建模型"""
    student_id: int = Field(..., description="学员ID")
    assessment_date: DateStr = Field(..., description="评估日期")
    coach_id: Optional[int] = Field(None, description="教练ID")
    
    # 9项能力评分（1-5分）
    technique: int = Field(..., ge=1, le=5, description="手法评分 (1-5)")
    footwork: int = Field(..., ge=1, le=5, description="步法评分 (1-5)")
    tactics: int = Field(..., ge=1, le=5, description="战术评分 (1-5)")
    power: int = Field(..., ge=1, le=5, description="力量评分 (1-5)")
    speed: int = Field(..., ge=1, le=5, description="速度评分 (1-5)")
    stamina: int = Field(..., ge=1, le=5, description="耐力评分 (1-5)")
    offense: int = Field(..., ge=1, le=5, description="进攻评分 (1-5)")
    defense: int = Field(..., ge=1, le=5, description="防守评分 (1-5)")
    mental: int = Field(..., ge=1, le=5, description="心理评分 (1-5)")
    
    # 综合评分（自动计算）
    overall_score: float = Field(0.0, description="综合评分（9项能力的平均值）")
    
    comments: Optional[str] = Field(None, description="教练评语")

    @field_validator('student_id', 'coach_id')
    @classmethod
    def validate_ids(cls, v: Optional[int]) -> Optional[int]:
        """验证ID"""
        if v is not None and v <= 0:
            raise ValueError('ID必须大于0')
        return v

    @field_validator('assessment_date')
    @classmethod
    def validate_assessment_date(cls, v: DateStr) -> DateStr:
        """验证评估日期"""
        if v > date.today():
            raise ValueError('评估日期不能晚于今天')
        return v

    @model_validator(mode='after')
    def calculate_overall_score(self):
        """计算综合评分（9项能力的平均值）"""
        scores = [
            self.technique, self.footwork, self.tactics,
            self.power, self.speed, self.stamina,
            self.offense, self.defense, self.mental
        ]
        self.overall_score = sum(scores) / len(scores)
        return self

class AbilityAssessmentUpdateSchema(AbilityAssessmentCreateSchema):
    """能力评估更新模型"""
    student_id: Optional[int] = Field(None, description="学员ID")
    assessment_date: Optional[DateStr] = Field(None, description="评估日期")

class AbilityAssessmentOutSchema(AbilityAssessmentCreateSchema, BaseSchema, UserBySchema):
    """能力评估响应模型"""
    overall_score: float = Field(..., description="综合评分")
    student: Optional['StudentOutSchema'] = Field(None, description="学员信息")
    coach: Optional[UserOutSchema] = Field(None, description="教练信息")

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

class AbilityAssessmentQueryParam:
    """能力评估查询参数"""
    def __init__(
        self,
        student_id: Optional[int] = Query(None, description="学员ID"),
        coach_id: Optional[int] = Query(None, description="教练ID"),
        min_overall_score: Optional[float] = Query(None, description="最小综合评分"),
        max_overall_score: Optional[float] = Query(None, description="最大综合评分"),
        assessment_date_start: Optional[DateStr] = Query(None, description="评估开始日期"),
        assessment_date_end: Optional[DateStr] = Query(None, description="评估结束日期"),
        created_time: Optional[list[DateTimeStr]] = Query(None, description="创建时间范围"),
        updated_time: Optional[list[DateTimeStr]] = Query(None, description="更新时间范围")
    ) -> None:
        # 精确查询字段
        if student_id is not None and not hasattr(student_id, 'field_info'):
            self.student_id = ("eq", student_id)
        if coach_id is not None and not hasattr(coach_id, 'field_info'):
            self.coach_id = ("eq", coach_id)
        
        # 范围查询字段
        if min_overall_score is not None:
            self.overall_score = ("ge", min_overall_score)
        if max_overall_score is not None:
            self.overall_score = ("le", max_overall_score)
        
        # 日期范围查询
        if assessment_date_start and assessment_date_end:
            self.assessment_date = ("between", (assessment_date_start, assessment_date_end))
        elif assessment_date_start:
            self.assessment_date = ("ge", assessment_date_start)
        elif assessment_date_end:
            self.assessment_date = ("le", assessment_date_end)
        
        # 时间范围查询
        if created_time and isinstance(created_time, list) and len(created_time) == 2:
            self.created_time = ("between", (created_time[0], created_time[1]))
        if updated_time and isinstance(updated_time, list) and len(updated_time) == 2:
            self.updated_time = ("between", (updated_time[0], updated_time[1]))
