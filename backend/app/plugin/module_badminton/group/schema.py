"""
group模块 - Schema定义
"""

from typing import Optional

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.api.v1.module_system.user.schema import UserOutSchema
from app.core.base_schema import BaseSchema, CommonSchema, UserBySchema
from app.core.validator import DateTimeStr

from ..student.schema import StudentOutSchema

# 简化的类型别名
CommonType = CommonSchema


# ============================================================================
# 能力分组相关 Schema
# ============================================================================

class AbilityGroupCreateSchema(BaseModel):
    """能力分组创建模型"""
    name: str = Field(..., min_length=1, max_length=64, description='分组名称')
    description: Optional[str] = Field(None, description='备注说明')
    coach_ids: list[int] = Field(default_factory=list, description='教练ID列表')
    student_ids: list[int] = Field(default_factory=list, description='学员ID列表')

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """验证分组名称"""
        v = v.strip()
        if not v:
            raise ValueError('分组名称不能为空')
        if len(v) > 64:
            raise ValueError('分组名称长度不能超过64个字符')
        return v


class AbilityGroupUpdateSchema(BaseModel):
    """能力分组更新模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=64, description='分组名称')
    description: Optional[str] = Field(None, description='备注说明')
    coach_ids: Optional[list[int]] = Field(None, description='教练ID列表')
    student_ids: Optional[list[int]] = Field(None, description='学员ID列表')

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """验证分组名称"""
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError('分组名称不能为空')
        if len(v) > 64:
            raise ValueError('分组名称长度不能超过64个字符')
        return v


class AbilityGroupOutSchema(BaseModel):
    """能力分组输出模型"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    coach_count: int = 0
    student_count: int = 0
    coaches: list[CommonType] = []
    students: list[CommonType] = []
    created_by: Optional[UserBySchema] = None
    updated_by: Optional[UserBySchema] = None
    created_time: Optional[DateTimeStr] = None
    updated_time: Optional[DateTimeStr] = None


class AbilityGroupSimpleOutSchema(BaseModel):
    """能力分组简单输出模型（用于下拉选择等）"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    student_count: int = 0


# ============================================================================
# 查询参数类
# ============================================================================

class AbilityGroupQueryParam:
    """能力分组查询参数"""
    def __init__(
        self,
        name: Optional[str] = Query(None, description="分组名称（模糊查询）"),
        coach_id: Optional[int] = Query(None, description="教练ID"),
        student_id: Optional[int] = Query(None, description="学员ID"),
        created_time: Optional[list[DateTimeStr]] = Query(None, description="创建时间范围"),
        updated_time: Optional[list[DateTimeStr]] = Query(None, description="更新时间范围"),
        created_id: Optional[int] = Query(None, description="创建人ID"),
        updated_id: Optional[int] = Query(None, description="更新人ID"),
    ) -> None:
        # 模糊查询字段
        if name:
            self.name = ("like", f"%{name}%")
        if coach_id:
            self.coach_id = ("eq", coach_id)
        if student_id:
            self.student_id = ("eq", student_id)
        if created_time and len(created_time) == 2:
            self.created_time = ("between", created_time)
        if updated_time and len(updated_time) == 2:
            self.updated_time = ("between", updated_time)
        if created_id:
            self.created_id = ("eq", created_id)
        if updated_id:
            self.updated_id = ("eq", updated_id)