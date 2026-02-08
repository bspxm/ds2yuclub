"""
schedule模块 - CRUD数据操作层
"""

from typing import Optional, List, Dict, Any, Sequence
from sqlalchemy import text, select, func, or_
from sqlalchemy.sql.expression import literal_column

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

    async def get_by_id_crud(self, id: int, preload: Optional[list[str]] = None) -> Optional[ClassScheduleListView]:
        """获取排课记录详情（使用视图，已包含班级和教练信息）"""
        return await self.get(id=id, preload=preload)

    async def page_crud(self, offset: int, limit: int, order_by: list[dict[str, str]], search: dict, out_schema: type = None, preload: list[str] | None = None) -> dict:
        """排课记录分页查询（使用视图）"""
        return await self.page(offset=offset, limit=limit, order_by=order_by, search=search, out_schema=out_schema, preload=preload)


# ============================================================================
# 教练排课视图 CRUD
# ============================================================================

class CoachScheduleCRUD(CRUDBase[None, None, None]):
    """教练排课视图查询（使用 view_badminton_coach_schedule_students 视图）"""

    def __init__(self, auth: AuthSchema) -> None:
        # 使用视图而不是模型
        super().__init__(model=None, auth=auth)
        self.table_name = "view_badminton_coach_schedule_students"

    async def list_crud(self, search: Optional[dict] = None, order_by: Optional[list[dict]] = None) -> Sequence:
        """
        从教练排课视图中查询排课列表
        
        Args:
            search: 搜索条件字典
            order_by: 排序条件列表
        
        Returns:
            排课记录列表
        """
        try:
            # 使用 SQLAlchemy 的 text 查询视图
            from sqlalchemy import text
            
            # 构建基础查询
            query_str = f"SELECT * FROM {self.table_name} WHERE 1=1"
            params = {}
            
            # 添加搜索条件
            if search:
                for key, (operator, value) in search.items():
                    if value is not None:
                        param_name = f"param_{len(params)}"
                        if operator == "eq":
                            query_str += f" AND {key} = :{param_name}"
                            params[param_name] = value
                        elif operator == "ne":
                            query_str += f" AND {key} != :{param_name}"
                            params[param_name] = value
                        elif operator == "like":
                            query_str += f" AND {key} LIKE :{param_name}"
                            params[param_name] = f"%{value}%"
                        elif operator == "in":
                            # IN 操作需要特殊处理
                            placeholders = [f":{param_name}_{i}" for i in range(len(value))]
                            query_str += f" AND {key} IN ({', '.join(placeholders)})"
                            for i, v in enumerate(value):
                                params[f"{param_name}_{i}"] = v
                        elif operator == "between":
                            query_str += f" AND {key} BETWEEN :{param_name}_start AND :{param_name}_end"
                            params[f"{param_name}_start"] = value[0]
                            params[f"{param_name}_end"] = value[1]
            
            # 添加排序条件
            if order_by:
                order_clauses = []
                for order in order_by:
                    for key, direction in order.items():
                        order_clauses.append(f"{key} {direction.upper()}")
                query_str += f" ORDER BY {', '.join(order_clauses)}"
            
            # 执行查询（使用命名参数）
            result = await self.auth.db.execute(text(query_str), params)
            rows = result.fetchall()
            
            # 转换为字典列表
            columns = result.keys()
            return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            from app.core.exceptions import CustomException
            raise CustomException(msg=f"教练排课视图查询失败: {e!s}")