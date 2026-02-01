"""
semester模块 - CRUD数据操作层
"""

from typing import Optional, List, Dict, Any, Sequence

from sqlalchemy import select, update as sql_update

from app.api.v1.module_system.auth.schema import AuthSchema
from app.core.base_crud import CRUDBase
from app.core.database import SessionDep

from .model import *
from .view_model import SemesterListView
from .schema import SemesterCreateSchema, SemesterUpdateSchema

# ============================================================================
# 学期 CRUD
# ============================================================================

class SemesterCRUD(CRUDBase[SemesterModel, SemesterCreateSchema, SemesterUpdateSchema]):
    """学期数据层"""

    def __init__(self, auth: AuthSchema) -> None:
        super().__init__(model=SemesterModel, auth=auth)

    async def get_by_id_crud(self, id: int, preload: Optional[list[str]] = None) -> Optional[SemesterModel]:
        """获取学期详情"""
        return await self.get(id=id, preload=preload)

    async def list_crud(self, search: Optional[dict] = None, order_by: Optional[list[dict]] = None, preload: Optional[list[str]] = None) -> Sequence[SemesterModel]:
        """学期列表"""
        return await self.list(search=search, order_by=order_by, preload=preload)

    async def create_crud(self, data: SemesterCreateSchema) -> Optional[SemesterModel]:
        """创建学期"""
        return await self.create(data=data)

    async def update_crud(self, id: int, data: SemesterUpdateSchema) -> Optional[SemesterModel]:
        """更新学期（优化版，避免刷新关联关系）"""
        from datetime import datetime
        
        obj_dict = data if isinstance(data, dict) else data.model_dump(exclude_unset=True, exclude={"id"})
        
        # 使用原始 SQL UPDATE 语句，避免加载对象和关联关系
        if obj_dict:
            # 添加更新时间
            obj_dict['updated_time'] = datetime.now()
            
            # 构建UPDATE语句
            stmt = sql_update(self.model).where(self.model.id == id).values(obj_dict)
            await self.auth.db.execute(stmt)
            await self.auth.db.flush()
            
            # 只查询更新后的对象（不预加载关联关系）
            result = await self.auth.db.execute(
                select(self.model).where(self.model.id == id)
            )
            semester = result.scalar_one()
            
            return semester
        else:
            # 没有要更新的字段，直接返回现有对象
            result = await self.auth.db.execute(
                select(self.model).where(self.model.id == id)
            )
            return result.scalar_one()

    async def delete_crud(self, ids: list[int]) -> None:
        """删除学期"""
        return await self.delete(ids=ids)

    async def page_crud(self, offset: int, limit: int, order_by: list[dict[str, str]], search: dict, out_schema: type, preload: list[str] | None = None) -> dict:
        """学期分页查询"""
        return await self.page(offset=offset, limit=limit, order_by=order_by, search=search, out_schema=out_schema, preload=preload)


class SemesterListCRUD(CRUDBase[SemesterListView, None, None]):
    """学期列表查询（使用视图模型，优化性能）"""

    def __init__(self, auth: AuthSchema) -> None:
        super().__init__(model=SemesterListView, auth=auth)

    async def get_by_id_crud(self, id: int, preload: Optional[list[str]] = None) -> Optional[SemesterListView]:
        """获取学期详情（使用视图）"""
        return await self.get(id=id, preload=preload)

    async def page_crud(self, offset: int, limit: int, order_by: list[dict[str, str]], search: dict, out_schema: type = None, preload: list[str] | None = None) -> dict:
        """学期分页查询（使用视图）"""
        return await self.page(offset=offset, limit=limit, order_by=order_by, search=search, out_schema=out_schema, preload=preload)
