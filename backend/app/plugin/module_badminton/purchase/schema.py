"""
purchase模块 - Schema定义
"""

from datetime import date, datetime, time
from typing import Optional

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator, model_serializer

from app.api.v1.module_system.user.schema import UserOutSchema
from app.core.base_schema import BaseSchema, UserBySchema
from app.core.validator import DateStr, DateTimeStr, TimeStr

from ..enums import (
    PurchaseStatusEnum,
    PurchaseTypeEnum
)

class PurchaseCreateSchema(BaseModel):
    """购买记录创建模型"""
    student_id: int = Field(..., description='学员ID')
    class_id: int = Field(..., description='班级ID')
    semester_id: int = Field(..., description='学期ID')
    purchase_date: DateStr = Field(..., description='购买日期')
    total_sessions: int = Field(..., description='购买总课时')
    valid_from: DateStr = Field(..., description='有效期开始')
    valid_until: DateStr = Field(..., description='有效期截止')
    original_price: float = Field(..., description='原价')
    actual_price: float = Field(..., description='实付价格')
    discount_rate: float = Field(default=1.0, description='折扣率')
    purchase_notes: Optional[str] = Field(None, description='购买备注')

class PurchaseUpdateSchema(PurchaseCreateSchema):
    """购买记录更新模型"""
    student_id: Optional[int] = Field(None, description='学员ID')
    class_id: Optional[int] = Field(None, description='班级ID')
    semester_id: Optional[int] = Field(None, description='学期ID')
    purchase_date: Optional[DateStr] = Field(None, description='购买日期')
    total_sessions: Optional[int] = Field(None, description='购买总课时')
    valid_from: Optional[DateStr] = Field(None, description='有效期开始')
    valid_until: Optional[DateStr] = Field(None, description='有效期截止')

class PurchaseOutSchema(PurchaseCreateSchema, BaseSchema, UserBySchema):
    """购买记录响应模型"""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class PurchaseQueryParam:
    """购买记录查询参数"""
    def __init__(
        self,
        student_id: Optional[int] = Query(None, description="学员ID"),
        semester_id: Optional[int] = Query(None, description="学期ID"),
        class_id: Optional[int] = Query(None, description="班级ID"),
        purchase_type: Optional[PurchaseTypeEnum] = Query(None, description="购买类型"),
        status: Optional[PurchaseStatusEnum] = Query(None, description="购买状态"),
        purchase_date_start: Optional[str] = Query(None, description="购买日期范围-起始"),
        purchase_date_end: Optional[str] = Query(None, description="购买日期范围-结束"),
        created_time: Optional[list[DateTimeStr]] = Query(None, description="创建时间范围"),
        updated_time: Optional[list[DateTimeStr]] = Query(None, description="更新时间范围")
    ) -> None:
        # 精确查询字段
        if student_id is not None and not hasattr(student_id, 'field_info'):
            self.student_id = ("eq", student_id)
        if semester_id is not None and not hasattr(semester_id, 'field_info'):
            self.semester_id = ("eq", semester_id)
        if class_id is not None and not hasattr(class_id, 'field_info'):
            self.class_id = ("eq", class_id)
        if purchase_type:
            self.purchase_type = ("eq", purchase_type)
        if status:
            self.status = ("eq", status)
        
        # 日期范围查询
        if purchase_date_start and purchase_date_end:
            self.purchase_date = ("between", (purchase_date_start, purchase_date_end))
        elif purchase_date_start:
            self.purchase_date = ("ge", purchase_date_start)
        elif purchase_date_end:
            self.purchase_date = ("le", purchase_date_end)
        
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
