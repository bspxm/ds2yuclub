"""
class_模块 - CRUD数据操作层
"""

from typing import Optional, List, Dict, Any, Sequence

from app.api.v1.module_system.auth.schema import AuthSchema
from app.core.base_crud import CRUDBase
from app.core.database import SessionDep

from .model import *
from .schema import (
    ClassCreateSchema,
    ClassUpdateSchema,
    ClassAttendanceCreateSchema,
    ClassAttendanceUpdateSchema
)

# ============================================================================
# 班级 CRUD
# ============================================================================

class ClassCRUD(CRUDBase[ClassModel, ClassCreateSchema, ClassUpdateSchema]):
    """班级数据层"""

    def __init__(self, auth: AuthSchema) -> None:
        super().__init__(model=ClassModel, auth=auth)

    async def get_by_id_crud(self, id: int, preload: Optional[list[str]] = None) -> Optional[ClassModel]:
        """获取班级详情"""
        return await self.get(id=id, preload=preload)

    async def list_crud(self, search: Optional[dict] = None, order_by: Optional[list[dict]] = None, preload: Optional[list[str]] = None) -> Sequence[ClassModel]:
        """班级列表"""
        return await self.list(search=search, order_by=order_by, preload=preload)

    async def create_crud(self, data: ClassCreateSchema) -> Optional[ClassModel]:
        """创建班级"""
        return await self.create(data=data)

    async def update_crud(self, id: int, data: ClassUpdateSchema) -> Optional[ClassModel]:
        """更新班级"""
        return await self.update(id=id, data=data)

    async def delete_crud(self, ids: list[int]) -> None:
        """删除班级"""
        return await self.delete(ids=ids)

    async def page_crud(self, offset: int, limit: int, order_by: list[dict[str, str]], search: dict, out_schema: type, preload: list[str] | None = None) -> dict:
        """班级分页查询"""
        return await self.page(offset=offset, limit=limit, order_by=order_by, search=search, out_schema=out_schema, preload=preload)
