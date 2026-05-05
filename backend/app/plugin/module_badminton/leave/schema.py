"""
leave模块 - Schema定义
"""

from datetime import date, datetime, time
from typing import Optional

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator, model_serializer

from app.api.v1.module_system.user.schema import UserOutSchema
from app.core.base_schema import BaseSchema, UserBySchema
from app.core.validator import DateStr, DateTimeStr, TimeStr

from ..enums import (
    LeaveStatusEnum
)

class LeaveRequestCreateSchema(BaseModel):
    """请假申请创建模型"""
    student_id: int = Field(..., description="学员ID")
    leave_date: DateStr = Field(..., description="请假日期")
    reason: str = Field(..., description="请假原因")
