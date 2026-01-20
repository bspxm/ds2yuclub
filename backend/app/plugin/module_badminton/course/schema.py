"""
course模块 - Schema定义
"""

from datetime import date, datetime, time
from typing import Optional

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator, model_serializer

from app.api.v1.module_system.user.schema import UserOutSchema
from app.core.base_schema import BaseSchema, UserBySchema
from app.core.validator import DateStr, DateTimeStr, TimeStr

from ..enums import (
    CourseTypeEnum
)

# ============================================================================
# 其他模型 Schema（简略版）
# ============================================================================

class CourseCreateSchema(BaseModel):
    """课程创建模型"""
    name: str = Field(..., description="课程名称")
    course_type: CourseTypeEnum = Field(default=CourseTypeEnum.REGULAR, description="课程类型")
    coach_id: Optional[int] = Field(None, description="教练ID")
    assistant_coach_id: Optional[int] = Field(None, description="助理教练ID")
    campus: Optional[str] = Field(None, description="所属校区")
    court_number: Optional[str] = Field(None, description="场地号")
    start_time: DateTimeStr = Field(..., description="开始时间")
    end_time: DateTimeStr = Field(..., description="结束时间")
    max_students: Optional[int] = Field(None, description="最大学员数")
    min_students: Optional[int] = Field(None, description="最小学员数")
    price: Optional[float] = Field(None, description="价格")
    notes: Optional[str] = Field(None, description="备注")
