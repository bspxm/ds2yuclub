"""
group模块 - CRUD数据操作层
"""

from typing import Optional, Sequence

from sqlalchemy import select, delete, update
from sqlalchemy.orm import selectinload

from app.api.v1.module_system.auth.schema import AuthSchema
from app.core.base_crud import CRUDBase
from app.core.database import async_db_session

from .model import *
from ..student.model import StudentModel
from .schema import (
    AbilityGroupCreateSchema,
    AbilityGroupUpdateSchema
)


# ============================================================================
# 能力分组 CRUD
# ============================================================================

class AbilityGroupCRUD(CRUDBase[AbilityGroupModel, AbilityGroupCreateSchema, AbilityGroupUpdateSchema]):
    """能力分组数据层"""

    def __init__(self, auth: AuthSchema) -> None:
        super().__init__(model=AbilityGroupModel, auth=auth)

    async def get_by_id_crud(self, id: int, preload: Optional[list[str]] = None) -> Optional[AbilityGroupModel]:
        """获取分组详情"""
        return await self.get(id=id, preload=preload)

    async def list_crud(self, search: Optional[dict] = None, order_by: Optional[list[dict]] = None, preload: Optional[list[str]] = None) -> Sequence[AbilityGroupModel]:
        """分组列表"""
        return await self.list(search=search, order_by=order_by, preload=preload)

    async def create_crud(self, data: AbilityGroupCreateSchema) -> Optional[AbilityGroupModel]:
        """创建分组"""
        obj_dict = data.model_dump()
        
        # 处理教练和学员关联
        coach_ids = obj_dict.pop('coach_ids', [])
        student_ids = obj_dict.pop('student_ids', [])
        
        # 在同一个会话中完成所有操作
        async with async_db_session() as db:
            # 创建分组
            group = AbilityGroupModel(**obj_dict)
            db.add(group)
            await db.flush()  # 刷新但不提交，获取 group.id
            
            # 添加教练关联
            for coach_id in coach_ids:
                group_coach = GroupCoachModel(group_id=group.id, coach_id=coach_id)
                db.add(group_coach)
            
            # 添加学员关联
            for student_id in student_ids:
                group_student = GroupStudentModel(group_id=group.id, student_id=student_id)
                db.add(group_student)
            
            # 提交所有更改
            await db.commit()
            
            # 预加载第一层关联关系，避免会话关闭后出现 DetachedInstanceError
            # 简化预加载，只加载 coaches 和 students，不加载嵌套的 created_by/updated_by
            from sqlalchemy.orm import selectinload
            
            stmt = (
                select(AbilityGroupModel)
                .options(
                    selectinload(AbilityGroupModel.coaches),
                    selectinload(AbilityGroupModel.students),
                )
                .where(AbilityGroupModel.id == group.id)
            )
            result = await db.execute(stmt)
            group = result.scalar_one()
        
        return group

    async def update_crud(self, id: int, data: AbilityGroupUpdateSchema) -> Optional[AbilityGroupModel]:
        """更新分组"""
        obj_dict = data.model_dump(exclude_unset=True, exclude={"id"})
        
        # 处理教练和学员关联
        coach_ids = obj_dict.pop('coach_ids', None)
        student_ids = obj_dict.pop('student_ids', None)
        
        # 更新分组基本信息
        group = await self.update(id=id, data=obj_dict)
        
        if group:
            async with async_db_session() as db:
                # 如果提供了教练ID列表，更新教练关联
                if coach_ids is not None:
                    # 删除旧的教练关联
                    stmt = delete(GroupCoachModel).where(GroupCoachModel.group_id == id)
                    await db.execute(stmt)
                    # 添加新的教练关联
                    for coach_id in coach_ids:
                        group_coach = GroupCoachModel(group_id=id, coach_id=coach_id)
                        db.add(group_coach)
                
                # 如果提供了学员ID列表，更新学员关联
                if student_ids is not None:
                    # 删除旧的学员关联
                    stmt = delete(GroupStudentModel).where(GroupStudentModel.group_id == id)
                    await db.execute(stmt)
                    # 添加新的学员关联
                    for student_id in student_ids:
                        group_student = GroupStudentModel(group_id=id, student_id=student_id)
                        db.add(group_student)
                
                await db.commit()
                
                # 预加载第一层关联关系，避免会话关闭后出现 DetachedInstanceError
                # 简化预加载，只加载 coaches 和 students，不加载嵌套的 created_by/updated_by
                from sqlalchemy.orm import selectinload
                
                stmt = (
                    select(AbilityGroupModel)
                    .options(
                        selectinload(AbilityGroupModel.coaches),
                        selectinload(AbilityGroupModel.students),
                    )
                    .where(AbilityGroupModel.id == id)
                )
                result = await db.execute(stmt)
                group = result.scalar_one()
        
        return group

    async def delete_crud(self, ids: list[int]) -> None:
        """删除分组"""
        return await self.delete(ids=ids)

    async def page_crud(self, offset: int, limit: int, order_by: Optional[list[dict]] = None, search: Optional[dict] = None, preload: Optional[list] = None, out_schema: Optional[type] = None) -> dict:
        """分组分页"""
        return await self.page(offset=offset, limit=limit, order_by=order_by, search=search, preload=preload, out_schema=out_schema)

    async def get_by_name_crud(self, name: str) -> Optional[AbilityGroupModel]:
        """根据名称查找分组"""
        return await self.get(name=name)

    async def get_students_by_group_crud(self, group_id: int) -> Sequence[StudentModel]:
        """获取分组下的所有学员"""
        async with async_db_session() as db:
            stmt = (
                select(StudentModel)
                .join(GroupStudentModel, StudentModel.id == GroupStudentModel.student_id)
                .where(GroupStudentModel.group_id == group_id)
                .order_by(StudentModel.id)
            )
            result = await db.execute(stmt)
            return result.scalars().all()
    async def get_coaches_by_role_crud(self, role_name: str = "教练") -> Sequence:
        """根据角色获取教练列表"""
        async with async_db_session() as db:
            from app.api.v1.module_system.user.model import UserModel, UserRolesModel
            from app.api.v1.module_system.role.model import RoleModel
            
            stmt = (
                select(UserModel)
                .join(UserRolesModel, UserModel.id == UserRolesModel.user_id)
                .join(RoleModel, UserRolesModel.role_id == RoleModel.id)
                .where((RoleModel.name == role_name) | (RoleModel.code == role_name))
                .order_by(UserModel.id)
            )
            result = await db.execute(stmt)
            return result.scalars().all()

    async def get_students_without_group_crud(self, exclude_group_id: Optional[int] = None) -> Sequence[StudentModel]:
        """获取未分组的学员或可重新分组的学员"""
        async with async_db_session() as db:
            if exclude_group_id:
                # 获取不属于当前分组的学员（可以来自其他分组或未分组）
                # 构建子查询：获取属于当前分组的学员ID
                subquery = (
                    select(GroupStudentModel.student_id)
                    .where(GroupStudentModel.group_id == exclude_group_id)
                )
                stmt = (
                    select(StudentModel)
                    .where(StudentModel.id.notin_(subquery))
                    .order_by(StudentModel.id)
                )
            else:
                # 获取所有未分组的学员
                # 构建子查询：获取所有已分组的学员ID
                subquery = (
                    select(GroupStudentModel.student_id.distinct())
                )
                stmt = (
                    select(StudentModel)
                    .where(StudentModel.id.notin_(subquery))
                    .order_by(StudentModel.id)
                )
            result = await db.execute(stmt)
            return result.scalars().all()