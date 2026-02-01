"""
schedule模块 - CRUD数据操作层
"""

from typing import Optional, List, Dict, Any, Sequence

from app.api.v1.module_system.auth.schema import AuthSchema
from app.core.base_crud import CRUDBase
from app.core.database import SessionDep

from .model import *
from .view_model import ClassScheduleListView
from ..class_.schema import ClassScheduleCreateV2Schema

# ============================================================================
# 排课记录 CRUD
# ============================================================================

class ClassScheduleCRUD(CRUDBase[ClassScheduleModel, ClassScheduleCreateV2Schema, ClassScheduleCreateV2Schema]):
    """排课记录数据层"""

    def __init__(self, auth: AuthSchema) -> None:
        super().__init__(model=ClassScheduleModel, auth=auth)

    async def get_by_id_crud(self, id: int, preload: Optional[list[str]] = None) -> Optional[ClassScheduleModel]:
        """获取排课记录详情"""
        return await self.get(id=id, preload=preload)

    async def list_crud(self, search: Optional[dict] = None, order_by: Optional[list[dict]] = None, preload: Optional[list[str]] = None) -> Sequence[ClassScheduleModel]:
        """排课记录列表"""
        return await self.list(search=search, order_by=order_by, preload=preload)

    async def create_crud(self, data: ClassScheduleCreateV2Schema | dict) -> Optional[ClassScheduleModel]:
        """创建排课记录"""
        return await self.create(data=data)

    async def update_crud(self, id: int, data: ClassScheduleCreateV2Schema) -> Optional[ClassScheduleModel]:
        """更新排课记录"""
        return await self.update(id=id, data=data)

    async def delete_crud(self, ids: list[int]) -> None:
        """删除排课记录"""
        return await self.delete(ids=ids)

    async def page_crud(self, offset: int, limit: int, order_by: list[dict[str, str]], search: dict, out_schema: type, preload: list[str] | None = None) -> dict:
        """排课记录分页查询"""
        return await self.page(offset=offset, limit=limit, order_by=order_by, search=search, out_schema=out_schema, preload=preload)


class ClassScheduleListCRUD(CRUDBase[ClassScheduleListView, None, None]):
    """排课记录列表查询（使用视图模型，优化性能）"""

    def __init__(self, auth: AuthSchema) -> None:
        super().__init__(model=ClassScheduleListView, auth=auth)

    async def page_crud(self, offset: int, limit: int, order_by: list[dict[str, str]], search: dict, out_schema: type = None, preload: list[str] | None = None) -> dict:
        """排课记录分页查询（使用视图）"""
        return await self.page(offset=offset, limit=limit, order_by=order_by, search=search, out_schema=out_schema, preload=preload)