"""
semester模块 - Schema定义
"""

from datetime import date, datetime, time
from typing import Optional

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_serializer, field_serializer

from app.api.v1.module_system.user.schema import UserOutSchema
from app.core.base_schema import BaseSchema, UserBySchema
from app.core.validator import DateStr, DateTimeStr, TimeStr

from ..enums import (
    SemesterTypeEnum,
    SemesterStatusEnum
)

# ============================================================================
# 学期制课时结算系统 Schema
# ============================================================================

class SemesterCreateSchema(BaseModel):
    """学期创建模型"""
    name: str = Field(..., description='学期名称')
    semester_type: SemesterTypeEnum = Field(default=SemesterTypeEnum.REGULAR, description='学期类型')
    start_date: date = Field(..., description='开始日期')
    end_date: date = Field(..., description='结束日期')
    week_count: int = Field(default=0, description='总周数')
    status: SemesterStatusEnum = Field(default=SemesterStatusEnum.PLANNING, description='学期状态')
    is_current: bool = Field(default=False, description='是否当前学期')
    settlement_date: Optional[date] = Field(None, description='结算日期')
    carry_over_enabled: bool = Field(default=True, description='允许课时结转')
    max_carry_over_sessions: int = Field(default=5, description='最大结转课时数')
    description: Optional[str] = Field(None, description='学期描述')

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """验证学期名称"""
        v = v.strip()
        if not v:
            raise ValueError('学期名称不能为空')
        if len(v) < 2 or len(v) > 64:
            raise ValueError('学期名称长度必须在2-64个字符之间')
        return v

    @field_validator('start_date', 'end_date', 'settlement_date')
    @classmethod
    def validate_date(cls, v: str | date) -> date:
        """验证日期字段，将字符串转换为date对象"""
        if isinstance(v, str):
            try:
                return datetime.strptime(v, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError('日期格式无效，请使用 YYYY-MM-DD 格式')
        return v

    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v: date, info) -> date:
        """验证结束日期"""
        start_date = info.data.get('start_date')
        if start_date and v < start_date:
            raise ValueError('结束日期不能早于开始日期')
        return v

class SemesterUpdateSchema(SemesterCreateSchema):
    """学期更新模型"""
    name: Optional[str] = Field(None, description='学期名称')
    semester_type: Optional[SemesterTypeEnum] = Field(None, description='学期类型')
    start_date: Optional[date] = Field(None, description='开始日期')
    end_date: Optional[date] = Field(None, description='结束日期')

class SemesterOutSchema(SemesterCreateSchema, BaseSchema, UserBySchema):
    """学期响应模型"""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True
    )

    @field_serializer('start_date', 'end_date', 'settlement_date')
    @classmethod
    def serialize_dates(cls, value: date | None) -> str | None:
        """序列化日期字段"""
        if value is None:
            return None
        return value.isoformat()


class SemesterQueryParam:
    """学期查询参数"""
    def __init__(
        self,
        name: Optional[str] = Query(None, description="学期名称"),
        semester_type: Optional[SemesterTypeEnum] = Query(None, description="学期类型"),
        status: Optional[SemesterStatusEnum] = Query(None, description="学期状态"),
        start_date_start: Optional[str] = Query(None, description="开始日期范围-起始"),
        start_date_end: Optional[str] = Query(None, description="开始日期范围-结束"),
        created_time: Optional[list[DateTimeStr]] = Query(None, description="创建时间范围"),
        updated_time: Optional[list[DateTimeStr]] = Query(None, description="更新时间范围")
    ) -> None:
        # 模糊查询字段
        if name:
            self.name = ("like", f"%{name}%")
        
        # 精确查询字段
        if semester_type:
            self.semester_type = ("eq", semester_type)
        if status:
            self.status = ("eq", status)
        
        # 日期范围查询
        if start_date_start and start_date_end:
            self.start_date = ("between", (start_date_start, start_date_end))
        elif start_date_start:
            self.start_date = ("ge", start_date_start)
        elif start_date_end:
            self.start_date = ("le", start_date_end)
        
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
