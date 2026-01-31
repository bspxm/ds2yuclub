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
    used_sessions: int = Field(default=0, description='已使用课时')
    remaining_sessions: int = Field(default=0, description='剩余课时')
    valid_from: date = Field(..., description='有效期开始')
    valid_until: date = Field(..., description='有效期截止')
    original_price: float = Field(..., description='原价')
    actual_price: float = Field(..., description='实付价格')
    discount_rate: float = Field(default=1.0, description='折扣率')
    purchase_notes: Optional[str] = Field(None, description='购买备注')
    status: str = Field(default='ACTIVE', description='购买状态')
    description: Optional[str] = Field(None, description='描述')
    selected_time_slots: Optional[dict[str, list[str]]] = Field(None, description='已选上课时间段（星期+代码格式）')

    @field_validator('selected_time_slots', mode='before')
    @classmethod
    def parse_time_slots(cls, value: Any) -> Optional[dict[str, list[str]]]:
        """解析时间段JSON字符串为字典"""
        if value is None:
            return None
        if isinstance(value, list):
            # 如果是空数组，返回 None
            if len(value) == 0:
                return None
            # 如果是非空数组，尝试保留兼容性
            return None
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            try:
                import json
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return None
                if isinstance(parsed, dict):
                    return parsed
                return None
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
    selected_time_slots: Optional[dict[str, list[str]]] = Field(None, description='已选上课时间段（星期+代码格式）')

    @field_validator('selected_time_slots', mode='before')
    @classmethod
    def parse_time_slots(cls, value: Any) -> Optional[dict[str, list[str]]]:
        """解析时间段JSON字符串为字典"""
        if value is None:
            return None
        if isinstance(value, list):
            return None
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            try:
                import json
                parsed = json.loads(value)
                if isinstance(parsed, dict):
                    return parsed
                return None
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
    selected_time_slots: Optional[dict[str, list[str]]] = Field(default=None, description='已选上课时间段（星期+代码格式）')

    # 字段验证器：将JSON字符串转换为列表
    @field_validator('selected_time_slots', mode='before')
    @classmethod
    def parse_time_slots(cls, value: Any) -> Optional[dict[str, list[str]]]:
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
    purchase_type: str = Field(default='new', description='购买类型')

    @model_serializer(mode='wrap')
    def serialize_model(self, handler: Any, _info: Any) -> dict[str, Any]:
        """自定义序列化，添加计算字段"""
        # 先调用默认的序列化器
        data = handler(self)

        # 转换所有 date 字段为字符串
        date_fields = ['purchase_date', 'valid_from', 'valid_until', 'created_time', 'updated_time', 'settlement_date']
        for field in date_fields:
            if field in data and hasattr(data[field], 'isoformat'):
                data[field] = data[field].isoformat()

        # 添加前端兼容的计算字段
        data['session_count'] = self.total_sessions
        data['unit_price'] = self.actual_price
        data['total_amount'] = self.actual_price * self.total_sessions
        data['start_date'] = self.valid_from.isoformat() if self.valid_from else None
        data['end_date'] = self.valid_until.isoformat() if self.valid_until else None
        
        # 确保 purchase_type 使用正确的枚举值
        if 'purchase_type' not in data or data['purchase_type'] not in ['new', 'renewal', 'carryover', 'upgrade']:
            data['purchase_type'] = 'new'

        # 确保 selected_time_slots 被正确序列化（从 JSON 字符串转换为字典）
        if 'selected_time_slots' not in data and hasattr(self, 'selected_time_slots'):
            data['selected_time_slots'] = self.selected_time_slots
        
        # 如果 selected_time_slots 是 JSON 字符串，转换为字典
        if 'selected_time_slots' in data and isinstance(data['selected_time_slots'], str):
            try:
                import json
                data['selected_time_slots'] = json.loads(data['selected_time_slots'])
            except (json.JSONDecodeError, ValueError):
                data['selected_time_slots'] = None

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