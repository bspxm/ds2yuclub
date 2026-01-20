"""
student模块 - CRUD数据操作层
"""

from typing import Optional, List, Dict, Any, Sequence, Sequence

from app.api.v1.module_system.auth.schema import AuthSchema
from app.core.base_crud import CRUDBase
from app.core.database import SessionDep

from .model import *
from .schema import (
    StudentCreateSchema,
    StudentUpdateSchema,
    ParentStudentCreateSchema,
    ParentStudentUpdateSchema,
    AbilityAssessmentCreateSchema,
    AbilityAssessmentUpdateSchema
)

# ============================================================================
# 学员 CRUD
# ============================================================================

class StudentCRUD(CRUDBase[StudentModel, StudentCreateSchema, StudentUpdateSchema]):
    """学员数据层"""

    def __init__(self, auth: AuthSchema) -> None:
        super().__init__(model=StudentModel, auth=auth)

    async def get_by_id_crud(self, id: int, preload: Optional[list[str]] = None) -> Optional[StudentModel]:
        """获取学员详情"""
        return await self.get(id=id, preload=preload)

    async def list_crud(self, search: Optional[dict] = None, order_by: Optional[list[dict]] = None, preload: Optional[list[str]] = None) -> Sequence[StudentModel]:
        """学员列表"""
        return await self.list(search=search, order_by=order_by, preload=preload)

    async def create_crud(self, data: StudentCreateSchema) -> Optional[StudentModel]:
        """创建学员"""
        # 将schema转换为字典
        obj_dict = data.model_dump()
        
        # 处理日期字段：将字符串转换为date对象
        date_fields = ['birth_date', 'join_date']
        for field in date_fields:
            if field in obj_dict and obj_dict[field] is not None:
                value = obj_dict[field]
                if isinstance(value, str):
                    # 字符串转换为date对象
                    try:
                        obj_dict[field] = datetime.strptime(value, '%Y-%m-%d').date()
                    except ValueError:
                        # 如果格式不匹配，尝试其他格式或保持原样
                        pass
        
        # 传递字典给基类的create方法
        return await self.create(data=obj_dict)

    async def update_crud(self, id: int, data: StudentUpdateSchema) -> Optional[StudentModel]:
        """更新学员"""
        # 将schema转换为字典
        obj_dict = data.model_dump(exclude_unset=True, exclude={"id"})
        
        # 处理日期字段：将字符串转换为date对象
        date_fields = ['birth_date', 'join_date']
        for field in date_fields:
            if field in obj_dict and obj_dict[field] is not None:
                value = obj_dict[field]
                if isinstance(value, str):
                    # 字符串转换为date对象
                    try:
                        obj_dict[field] = datetime.strptime(value, '%Y-%m-%d').date()
                    except ValueError:
                        # 如果格式不匹配，尝试其他格式或保持原样
                        pass
        
        # 传递字典给基类的update方法
        return await self.update(id=id, data=obj_dict)

    async def delete_crud(self, ids: list[int]) -> None:
        """删除学员"""
        return await self.delete(ids=ids)

    async def set_available_crud(self, ids: list[int], status: str) -> None:
        """设置学员状态"""
        return await self.set(ids=ids, status=status)

    async def page_crud(self, offset: int, limit: int, order_by: Optional[list[dict]] = None, search: Optional[dict] = None, preload: Optional[list] = None, out_schema: Optional[type] = None) -> dict:
        """学员分页"""
        return await self.page(offset=offset, limit=limit, order_by=order_by, search=search, preload=preload, out_schema=out_schema)

    async def get_by_name_crud(self, name: str) -> Optional[StudentModel]:
        """根据姓名查找学员"""
        return await self.get(name=name)

    async def get_by_group_crud(self, group_name: str) -> Sequence[StudentModel]:
        """根据组别查找学员"""
        return await self.list(search={"group_name": ("eq", group_name)})

    async def update_statistics_crud(self, student_id: int, won: bool = False) -> Optional[StudentModel]:
        """更新学员比赛统计信息"""
        student = await self.get_by_id_crud(student_id)
        if not student:
            return None
        
        student.total_matches += 1
        if won:
            student.wins += 1
        else:
            student.losses += 1
        
        if student.total_matches > 0:
            student.win_rate = round(student.wins / student.total_matches * 100, 2)
        
        return await self.update_crud(student_id, StudentUpdateSchema(
            total_matches=student.total_matches,
            wins=student.wins,
            losses=student.losses,
            win_rate=student.win_rate
        ))

# ============================================================================
# 家长-学员关联 CRUD
# ============================================================================

class ParentStudentCRUD(CRUDBase[ParentStudentModel, ParentStudentCreateSchema, ParentStudentUpdateSchema]):
    """家长-学员关联数据层"""

    def __init__(self, auth: AuthSchema) -> None:
        super().__init__(model=ParentStudentModel, auth=auth)

    async def get_by_id_crud(self, id: int, preload: Optional[list[str]] = None) -> Optional[ParentStudentModel]:
        """获取关联详情"""
        return await self.get(id=id, preload=preload)

    async def list_crud(self, search: Optional[dict] = None, order_by: Optional[list[dict]] = None, preload: Optional[list[str]] = None) -> Sequence[ParentStudentModel]:
        """关联列表"""
        return await self.list(search=search, order_by=order_by, preload=preload)

    async def create_crud(self, data: ParentStudentCreateSchema) -> Optional[ParentStudentModel]:
        """创建关联"""
        # 检查关联是否已存在
        existing = await self.get(
            parent_id=data.parent_id,
            student_id=data.student_id
        )
        if existing:
            raise ValueError("该家长-学员关联已存在")
        return await self.create(data=data)

    async def update_crud(self, id: int, data: ParentStudentUpdateSchema) -> Optional[ParentStudentModel]:
        """更新关联"""
        return await self.update(id=id, data=data)

    async def delete_crud(self, ids: list[int]) -> None:
        """删除关联"""
        return await self.delete(ids=ids)

    async def get_by_parent_id_crud(self, parent_id: int) -> Sequence[ParentStudentModel]:
        """根据家长ID查找关联"""
        return await self.list(search={"parent_id": ("eq", parent_id)})

    async def get_by_student_id_crud(self, student_id: int) -> Sequence[ParentStudentModel]:
        """根据学员ID查找关联"""
        return await self.list(search={"student_id": ("eq", student_id)})

    async def set_primary_crud(self, parent_student_id: int, is_primary: bool = True) -> Optional[ParentStudentModel]:
        """设置主要联系人"""
        return await self.update_crud(parent_student_id, ParentStudentUpdateSchema(is_primary=is_primary))

# ============================================================================
# 能力评估 CRUD
# ============================================================================

class AbilityAssessmentCRUD(CRUDBase[AbilityAssessmentModel, AbilityAssessmentCreateSchema, AbilityAssessmentUpdateSchema]):
    """能力评估数据层"""

    def __init__(self, auth: AuthSchema) -> None:
        super().__init__(model=AbilityAssessmentModel, auth=auth)

    async def get_by_id_crud(self, id: int, preload: Optional[list[str]] = None) -> Optional[AbilityAssessmentModel]:
        """获取评估详情"""
        return await self.get(id=id, preload=preload)

    async def list_crud(self, search: Optional[dict] = None, order_by: Optional[list[dict]] = None, preload: Optional[list[str]] = None) -> Sequence[AbilityAssessmentModel]:
        """评估列表"""
        return await self.list(search=search, order_by=order_by, preload=preload)

    async def create_crud(self, data: AbilityAssessmentCreateSchema) -> Optional[AbilityAssessmentModel]:
        """创建评估"""
        # 将schema转换为字典
        obj_dict = data.model_dump()
        
        # 处理日期字段：将字符串转换为date对象
        if 'assessment_date' in obj_dict and obj_dict['assessment_date'] is not None:
            value = obj_dict['assessment_date']
            if isinstance(value, str):
                # 字符串转换为date对象
                try:
                    obj_dict['assessment_date'] = datetime.strptime(value, '%Y-%m-%d').date()
                except ValueError:
                    # 如果格式不匹配，尝试其他格式或保持原样
                    pass
        
        # 传递字典给基类的create方法
        return await self.create(data=obj_dict)

    async def update_crud(self, id: int, data: AbilityAssessmentUpdateSchema) -> Optional[AbilityAssessmentModel]:
        """更新评估"""
        # 将schema转换为字典
        obj_dict = data.model_dump(exclude_unset=True, exclude={"id"})
        
        # 处理日期字段：将字符串转换为date对象
        if 'assessment_date' in obj_dict and obj_dict['assessment_date'] is not None:
            value = obj_dict['assessment_date']
            if isinstance(value, str):
                # 字符串转换为date对象
                try:
                    obj_dict['assessment_date'] = datetime.strptime(value, '%Y-%m-%d').date()
                except ValueError:
                    # 如果格式不匹配，尝试其他格式或保持原样
                    pass
        
        # 传递字典给基类的update方法
        return await self.update(id=id, data=obj_dict)

    async def delete_crud(self, ids: list[int]) -> None:
        """删除评估"""
        return await self.delete(ids=ids)

    async def get_latest_by_student_crud(self, student_id: int) -> Optional[AbilityAssessmentModel]:
        """获取学员最新评估"""
        assessments = await self.list(
            search={"student_id": ("eq", student_id)},
            order_by=[{"assessment_date": "desc"}],
            preload=["student", "coach"]
        )
        return assessments[0] if assessments else None

    async def get_by_student_crud(self, student_id: int, limit: int = 10) -> Sequence[AbilityAssessmentModel]:
        """获取学员评估历史"""
        return await self.list(
            search={"student_id": ("eq", student_id)},
            order_by=[{"assessment_date": "desc"}],
            preload=["coach"],
            limit=limit
        )

    async def page_crud(self, offset: int, limit: int, order_by: Optional[list[dict]] = None, search: Optional[dict] = None, preload: Optional[list] = None, out_schema: Optional[type] = None) -> dict:
        """评估分页"""
        return await self.page(offset=offset, limit=limit, order_by=order_by, search=search, preload=preload, out_schema=out_schema)
