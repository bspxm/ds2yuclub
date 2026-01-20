"""
通用响应模型
"""
from pydantic import BaseModel, Field


class SimpleResponse(BaseModel):
    """
    简单响应模型
    """
    success: bool = Field(..., description='是否成功')
    message: str = Field(..., description='响应消息')
    data: dict | None = Field(None, description='响应数据')