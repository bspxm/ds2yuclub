"""
class_模块 - Service服务层
"""

from datetime import date, datetime, timedelta
from typing import Optional, List, Dict, Any

from sqlalchemy.orm import Session

from app.api.v1.module_system.user.service import UserService
from app.core.base_crud import BaseCRUD
from app.core.database import SessionDep
from app.core.exceptions import CustomException
from app.core.logger import logger

from .model import *
from .crud import *
from .schema import *
from app.common.response import PaginatedResponse

from app.api.v1.module_system.auth.schema import AuthSchema

# ============================================================================
# 班级管理服务
# ============================================================================

class ClassService:
    """班级管理服务层"""

    @classmethod
    async def detail_service(cls, auth: AuthSchema, class_id: int) -> dict:
        """获取班级详情"""
        class_obj = await ClassCRUD(auth).get_by_id_crud(
            id=class_id,
            preload=["semester", "coach_user", "created_by", "updated_by"]
        )
        if not class_obj:
            raise CustomException(msg="班级不存在")
        return ClassOutSchema.model_validate(class_obj).model_dump()

    @classmethod
    async def list_service(cls, auth: AuthSchema, search: Optional[dict] = None, order_by: Optional[list[dict]] = None) -> list[dict]:
        """班级列表查询"""
        classes = await ClassCRUD(auth).list_crud(
            search=search,
            order_by=order_by,
            preload=["semester", "coach_user"]
        )
        return [ClassOutSchema.model_validate(class_obj).model_dump() for class_obj in classes]

    @classmethod
    async def page_service(cls, auth: AuthSchema, page_no: int, page_size: int, search: Optional[dict | ClassQueryParam] = None, order_by: Optional[list[dict]] = None) -> dict:
        """班级分页查询"""
        # 将QueryParam对象转换为字典
        if isinstance(search, ClassQueryParam):
            search_dict = vars(search)
        else:
            search_dict = search or {}
        
        order_by_list = order_by or [{'id': 'asc'}]
        offset = (page_no - 1) * page_size

        result = await ClassCRUD(auth).page_crud(
            offset=offset,
            limit=page_size,
            order_by=order_by_list,
            search=search_dict,
            preload=["semester", "coach_user"],
            out_schema=ClassOutSchema
        )
        
        return PaginatedResponse(
            total=result["total"],
            page_no=page_no,
            page_size=page_size,
            items=result["items"]
        ).model_dump()

    @classmethod
    async def create_service(cls, auth: AuthSchema, data: ClassCreateSchema) -> dict:
        """创建班级"""
        # 检查班级名称是否重复
        # TODO: 实现名称重复检查
        
        class_obj = await ClassCRUD(auth).create_crud(data=data)
        if not class_obj:
            raise CustomException(msg="创建班级失败")
        return SimpleResponse(
            success=True,
            message="班级创建成功",
            data=ClassOutSchema.model_validate(class_obj).model_dump()
        ).model_dump()

    @classmethod
    async def update_service(cls, auth: AuthSchema, class_id: int, data: ClassUpdateSchema) -> dict:
        """更新班级"""
        class_obj = await ClassCRUD(auth).update_crud(id=class_id, data=data)
        if not class_obj:
            raise CustomException(msg="班级不存在或更新失败")
        return SimpleResponse(
            success=True,
            message="班级更新成功",
            data=ClassOutSchema.model_validate(class_obj).model_dump()
        ).model_dump()

    @classmethod
    async def delete_service(cls, auth: AuthSchema, class_ids: list[int]) -> dict:
        """删除班级"""
        await ClassCRUD(auth).delete_crud(ids=class_ids)
        return SimpleResponse(
            success=True,
            message="班级删除成功"
        ).model_dump()
