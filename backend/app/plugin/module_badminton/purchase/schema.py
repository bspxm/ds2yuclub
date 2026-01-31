"""
purchase模块 - Schema定义
"""

from datetime import date, datetime, time
from typing import Any, Optional

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator, model_serializer, field_serializer, computed_field

from app.api.v1.module_system.user.schema import UserOutSchema
from app.core.base_schema import BaseSchema, UserBySchema
from app.core.validator import DateTimeStr, TimeStr

from ..enums import (
    PurchaseStatusEnum,
    PurchaseTypeEnum
)

class PurchaseCreateSchema(BaseModel):
    """购买记录创建模型"""
    student_id: int = Field(..., description='学员ID')
    class_id: int = Field(..., description='班级ID')
    semester_id: int = Field(..., description='学期ID')
    purchase_date: date = Field(..., description='购买日期')
    total_sessions: int = Field(..., description='购买总课时')
    valid_from: date = Field(..., description='有效期开始')
    valid_until: date = Field(..., description='有效期截止')
    original_price: float = Field(..., description='原价')
    actual_price: float = Field(..., description='实付价格')
    discount_rate: float = Field(default=1.0, description='折扣率')
    purchase_notes: Optional[str] = Field(None, description='购买备注')
    selected_time_slots: Optional[list[int]] = Field(None, description='已选上课时间段ID列表')

    @field_validator('selected_time_slots', mode='before')
    @classmethod
    def parse_time_slots(cls, value: Any) -> Optional[list[int]]:
        """解析时间段JSON字符串为列表"""
        if value is None:
            return None
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            try:
                import json
                return json.loads(value)
            except (json.JSONDecodeError, ValueError):
                return None
        return None

    @field_validator('purchase_date', 'valid_from', 'valid_until')
    @classmethod
    def validate_date(cls, v: str | date) -> date:
        """验证日期字段，将字符串转换为date对象"""
        if isinstance(v, str):
            try:
                return datetime.strptime(v, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError('日期格式无效，请使用 YYYY-MM-DD 格式')
        return v


class BatchPurchaseCreateSchema(BaseModel):
    """批量购买记录创建模型"""
    student_ids: list[int] = Field(..., description='学员ID列表')
    class_id: int = Field(..., description='班级ID')
    semester_id: int = Field(..., description='学期ID')
    purchase_date: date = Field(..., description='购买日期')
    total_sessions: int = Field(..., description='购买总课时')
    valid_from: date = Field(..., description='有效期开始')
    valid_until: date = Field(..., description='有效期截止')
    original_price: float = Field(..., description='原价')
    actual_price: float = Field(..., description='实付价格')
    discount_rate: float = Field(default=1.0, description='折扣率')
    purchase_notes: Optional[str] = Field(None, description='购买备注')
    selected_time_slots: Optional[list[int]] = Field(None, description='已选上课时间段ID列表')

    @field_validator('purchase_date', 'valid_from', 'valid_until')
    @classmethod
    def validate_date(cls, v: str | date) -> date:
        """验证日期字段，将字符串转换为date对象"""
        if isinstance(v, str):
            try:
                return datetime.strptime(v, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError('日期格式无效，请使用 YYYY-MM-DD 格式')
        return v

class PurchaseUpdateSchema(PurchaseCreateSchema):
    """购买记录更新模型"""
    student_id: Optional[int] = Field(None, description='学员ID')
    class_id: Optional[int] = Field(None, description='班级ID')
    semester_id: Optional[int] = Field(None, description='学期ID')
    purchase_date: Optional[date] = Field(None, description='购买日期')
    total_sessions: Optional[int] = Field(None, description='购买总课时')
    valid_from: Optional[date] = Field(None, description='有效期开始')
    valid_until: Optional[date] = Field(None, description='有效期截止')

class PurchaseOutSchema(PurchaseCreateSchema, BaseSchema, UserBySchema):
    """购买记录响应模型"""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True, populate_by_name=True)

    # 关联对象
    student: Optional[Any] = Field(default=None, description='学员信息')
    semester: Optional[Any] = Field(default=None, description='学期信息')
    class_ref: Optional[Any] = Field(default=None, description='班级信息')

    # 覆盖 selected_time_slots 字段，支持从数据库JSON字符串读取
    selected_time_slots: Optional[list[int]] = Field(default=None, description='已选上课时间段ID列表')

    # 字段验证器：将JSON字符串转换为列表
    @field_validator('selected_time_slots', mode='before')
    @classmethod
    def parse_time_slots(cls, value: Any) -> Optional[list[int]]:
        """解析时间段JSON字符串为列表"""
        if value is None:
            return None
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            try:
                import json
                return json.loads(value)
            except (json.JSONDecodeError, ValueError):
                return None
        return None

    # 序列化关联对象
    @field_serializer('student', 'semester', 'class_ref')
    @classmethod
    def serialize_related_object(cls, value: Any) -> Any:
        """序列化关联对象"""
        if value is None:
            return None
        if hasattr(value, '__table__'):
            return {
                'id': getattr(value, 'id', None),
                'name': getattr(value, 'name', None)
            }
        if isinstance(value, dict):
            return value
        if hasattr(value, 'model_dump'):
            return value.model_dump()
        return value

    # 添加前端兼容字段
    session_count: int = Field(default=0, description='课时数')
    unit_price: float = Field(default=0.0, description='单价')
    total_amount: float = Field(default=0.0, description='总金额')
    start_date: Optional[str] = Field(default=None, description='开始日期')
    end_date: Optional[str] = Field(default=None, description='结束日期')
    purchase_type: str = Field(default='package', description='购买类型')

    @model_serializer(mode='wrap')
    def serialize_model(self, handler: Any, _info: Any) -> dict[str, Any]:
        """自定义序列化，添加计算字段"""
        # 先调用默认的序列化器
        data = handler(self)

        # 添加前端兼容的计算字段
        data['session_count'] = self.total_sessions
        data['unit_price'] = self.actual_price
        data['total_amount'] = self.actual_price * self.total_sessions
        data['start_date'] = self.valid_from.isoformat() if self.valid_from else None
        data['end_date'] = self.valid_until.isoformat() if self.valid_until else None
        data['purchase_type'] = 'package'

        return data


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