"""
group模块 - Service服务层
"""
from typing import Optional

from pydantic import BaseModel

from sqlalchemy import update

from app.core.base_crud import BaseCRUD
from app.core.database import async_db_session
from app.core.exceptions import CustomException
from app.core.logger import logger

from .model import *
from .crud import *
from .schema import *
from app.common.response import PaginatedResponse
from ..response import SimpleResponse

from app.api.v1.module_system.auth.schema import AuthSchema
from app.core.base_schema import BatchSetAvailable


# ============================================================================
# 临时 Schema 用于处理 out_schema=None 的情况
# ============================================================================

class SimpleOutSchema(BaseModel):
    """简单的输出Schema，只包含id字段"""
    id: int


# ============================================================================
# 能力分组管理服务
# ============================================================================

class AbilityGroupService:
    """能力分组管理服务层"""

    @classmethod
    async def detail_service(cls, auth: AuthSchema, group_id: int) -> dict:
        """获取分组详情"""
        group = await AbilityGroupCRUD(auth).get_by_id_crud(
            id=group_id,
            preload=["coaches", "students", "created_by", "updated_by"]
        )
        if not group:
            raise CustomException(msg="分组不存在")
        
        # 手动构建返回数据，避免 Pydantic 自动访问懒加载属性
        # 确保 coaches 和 students 不为 None
        coaches = group.coaches if group.coaches is not None else []
        students = group.students if group.students is not None else []
        
        # 处理 datetime 对象
        created_time = group.created_time.isoformat() if group.created_time else None
        updated_time = group.updated_time.isoformat() if group.updated_time else None
        created_by = None
        updated_by = None
        
        if group.created_by:
            created_by = {'id': group.created_by.id, 'name': group.created_by.name}
        if group.updated_by:
            updated_by = {'id': group.updated_by.id, 'name': group.updated_by.name}
        
        result = {
            'id': group.id,
            'name': group.name,
            'description': group.description,
            'coach_count': len(coaches),
            'student_count': len(students),
            'coaches': [{'id': c.id, 'name': c.name} for c in coaches],
            'students': [{'id': s.id, 'name': s.name} for s in students],
            'created_by': created_by,
            'updated_by': updated_by,
            'created_time': created_time,
            'updated_time': updated_time
        }
        
        return result

    @classmethod
    async def list_service(cls, auth: AuthSchema, search: Optional[AbilityGroupQueryParam] = None, order_by: Optional[list[dict[str, str]]] = None) -> list[dict]:
        """分组列表查询"""
        search_dict = search.__dict__ if search else None
        groups = await AbilityGroupCRUD(auth).list_crud(
            search=search_dict,
            order_by=order_by,
            preload=["coaches", "students"]
        )
        
        # 手动构建返回数据，避免 Pydantic 自动访问懒加载属性
        results = []
        for group in groups:
            # 确保 coaches 和 students 不为 None
            coaches = group.coaches if group.coaches is not None else []
            students = group.students if group.students is not None else []
            
            # 处理 datetime 对象
            created_time = group.created_time.isoformat() if group.created_time else None
            updated_time = group.updated_time.isoformat() if group.updated_time else None
            
            result = {
                'id': group.id,
                'name': group.name,
                'description': group.description,
                'coach_count': len(coaches),
                'student_count': len(students),
                'coaches': [{'id': c.id, 'name': c.name} for c in coaches],
                'students': [{'id': s.id, 'name': s.name} for s in students],
                'created_time': created_time,
                'updated_time': updated_time
            }
            results.append(result)
        
        return results

    @classmethod
    async def page_service(cls, auth: AuthSchema, page_no: int, page_size: int, search: Optional[AbilityGroupQueryParam] = None, order_by: Optional[list[dict[str, str]]] = None) -> dict:
        """分组分页查询"""
        search_dict = search.__dict__ if search else {}
        order_by_list = order_by or [{'id': 'asc'}]
        offset = (page_no - 1) * page_size

        # 不使用 out_schema，直接获取原始模型对象
        result = await AbilityGroupCRUD(auth).page_crud(
            offset=offset,
            limit=page_size,
            order_by=order_by_list,
            search=search_dict,
            preload=["coaches", "students"],
            out_schema=None
        )

        # 手动构建返回数据，避免 Pydantic 自动访问懒加载属性
        items = []
        for group in result["items"]:
            # 确保 coaches 和 students 不为 None
            coaches = group.coaches if group.coaches is not None else []
            students = group.students if group.students is not None else []

            # 处理 datetime 对象
            created_time = group.created_time.isoformat() if group.created_time else None
            updated_time = group.updated_time.isoformat() if group.updated_time else None
            
            item = {
                'id': group.id,
                'name': group.name,
                'description': group.description,
                'coach_count': len(coaches),
                'student_count': len(students),
                'coaches': [{'id': c.id, 'name': c.name} for c in coaches],
                'students': [{'id': s.id, 'name': s.name} for s in students],
                'created_time': created_time,
                'updated_time': updated_time
            }
            items.append(item)
        
        return {
            "total": result["total"],
            "page_no": page_no,
            "page_size": page_size,
            "items": items
        }

    @classmethod
    async def create_service(cls, auth: AuthSchema, data: AbilityGroupCreateSchema) -> dict:
        """创建分组"""
        # 检查分组名称是否已存在
        existing = await AbilityGroupCRUD(auth).get_by_name_crud(data.name)
        if existing:
            raise CustomException(msg="创建失败，分组名称已存在")
        
        # 创建分组
        group = await AbilityGroupCRUD(auth).create_crud(data=data)
        if not group:
            raise CustomException(msg="创建失败")
        
        # 批量更新学员的 group_name 字段
        if data.student_ids:
            async with async_db_session() as db:
                from ..student.model import StudentModel
                stmt = (
                    update(StudentModel)
                    .where(StudentModel.id.in_(data.student_ids))
                    .values(group_name=data.name)
                )
                await db.execute(stmt)
                await db.commit()
                logger.info(f"已更新 {len(data.student_ids)} 名学员的组别为 {data.name}")
        
        # 手动构建返回数据
        # 确保 coaches 和 students 不为 None
        coaches = group.coaches if group.coaches is not None else []
        students = group.students if group.students is not None else []
        
        # 处理 datetime 对象
        created_time = group.created_time.isoformat() if group.created_time else None
        updated_time = group.updated_time.isoformat() if group.updated_time else None
        
        result = {
            'id': group.id,
            'name': group.name,
            'description': group.description,
            'coach_count': len(coaches),
            'student_count': len(students),
            'coaches': [{'id': c.id, 'name': c.name} for c in coaches],
            'students': [{'id': s.id, 'name': s.name} for s in students],
            'created_time': created_time,
            'updated_time': updated_time
        }
        
        return result

    @classmethod
    async def update_service(cls, auth: AuthSchema, group_id: int, data: AbilityGroupUpdateSchema) -> dict:
        """更新分组"""
        group = await AbilityGroupCRUD(auth).get_by_id_crud(group_id)
        if not group:
            raise CustomException(msg="分组不存在")
        
        # 如果修改了名称，检查是否与其他分组重名
        old_name = group.name
        if data.name and data.name != old_name:
            existing = await AbilityGroupCRUD(auth).get_by_name_crud(data.name)
            if existing and existing.id != group_id:
                raise CustomException(msg="更新失败，分组名称已存在")
        
        # 获取原始学员列表
        original_student_ids = [student.id for student in group.students]
        
        # 更新分组
        updated = await AbilityGroupCRUD(auth).update_crud(group_id, data=data)
        if not updated:
            raise CustomException(msg="更新失败")
        
        # 获取新的分组名称
        new_name = data.name if data.name else old_name
        
        # 处理学员关联变更
        if data.student_ids is not None:
            new_student_ids = set(data.student_ids)
            old_student_ids = set(original_student_ids)
            
            # 新增的学员
            added_students = new_student_ids - old_student_ids
            # 移除的学员
            removed_students = old_student_ids - new_student_ids
            
            async with async_db_session() as db:
                from ..student.model import StudentModel
                
                # 更新新增学员的 group_name
                if added_students:
                    stmt = (
                        update(StudentModel)
                        .where(StudentModel.id.in_(list(added_students)))
                        .values(group_name=new_name)
                    )
                    await db.execute(stmt)
                    logger.info(f"已更新 {len(added_students)} 名学员的组别为 {new_name}")
                
                # 清空移除学员的 group_name
                if removed_students:
                    stmt = (
                        update(StudentModel)
                        .where(StudentModel.id.in_(list(removed_students)))
                        .values(group_name=None)
                    )
                    await db.execute(stmt)
                    logger.info(f"已清空 {len(removed_students)} 名学员的组别")
                
                # 如果分组名称发生变化，更新所有当前学员的 group_name
                if new_name != old_name and new_student_ids:
                    stmt = (
                        update(StudentModel)
                        .where(StudentModel.id.in_(list(new_student_ids)))
                        .values(group_name=new_name)
                    )
                    await db.execute(stmt)
                    logger.info(f"已更新 {len(new_student_ids)} 名学员的组别从 {old_name} 变更为 {new_name}")
                
                await db.commit()
        
        # 手动构建返回数据
        # 确保 coaches 和 students 不为 None
        coaches = updated.coaches if updated.coaches is not None else []
        students = updated.students if updated.students is not None else []
        
        # 处理 datetime 对象
        created_time = updated.created_time.isoformat() if updated.created_time else None
        updated_time = updated.updated_time.isoformat() if updated.updated_time else None
        
        result = {
            'id': updated.id,
            'name': updated.name,
            'description': updated.description,
            'coach_count': len(coaches),
            'student_count': len(students),
            'coaches': [{'id': c.id, 'name': c.name} for c in coaches],
            'students': [{'id': s.id, 'name': s.name} for s in students],
            'created_time': created_time,
            'updated_time': updated_time
        }
        
        return result

    @classmethod
    async def delete_service(cls, auth: AuthSchema, group_ids: list[int]) -> dict:
        """删除分组"""
        # 检查分组是否存在并获取关联学员
        groups_to_delete = []
        all_student_ids = []
        
        for group_id in group_ids:
            group = await AbilityGroupCRUD(auth).get_by_id_crud(group_id)
            if not group:
                raise CustomException(msg=f"分组ID {group_id} 不存在")
            
            # 获取关联的学员ID
            student_ids = [student.id for student in group.students]
            if student_ids:
                all_student_ids.extend(student_ids)
            
            groups_to_delete.append(group)
        
        # 清空所有关联学员的 group_name 字段
        if all_student_ids:
            async with async_db_session() as db:
                from ..student.model import StudentModel
                stmt = (
                    update(StudentModel)
                    .where(StudentModel.id.in_(all_student_ids))
                    .values(group_name=None)
                )
                await db.execute(stmt)
                await db.commit()
                logger.info(f"已清空 {len(all_student_ids)} 名学员的组别")
        
        # 删除分组
        await AbilityGroupCRUD(auth).delete_crud(group_ids)
        
        return SimpleResponse(
            success=True,
            message=f"成功删除 {len(group_ids)} 个分组"
        ).model_dump()

    @classmethod
    async def get_coaches_service(cls, auth: AuthSchema) -> list[dict]:
        """获取教练列表（仅显示教练角色用户）"""
        coaches = await AbilityGroupCRUD(auth).get_coaches_by_role_crud(role_name="教练")
        return [
            {
                "id": coach.id,
                "name": coach.name,
                "mobile": coach.mobile
            }
            for coach in coaches
        ]

    @classmethod
    async def get_available_students_service(cls, auth: AuthSchema, exclude_group_id: Optional[int] = None) -> list[dict]:
        """获取可用学员列表"""
        students = await AbilityGroupCRUD(auth).get_students_without_group_crud(exclude_group_id=exclude_group_id)
        return [
            {
                "id": student.id,
                "name": student.name,
                "gender": student.gender.value if student.gender else None,
                "age": cls._calculate_age(student.birth_date) if student.birth_date else None,
                "level": student.level,
                "group_name": student.group_name
            }
            for student in students
        ]

    @classmethod
    def _calculate_age(cls, birth_date) -> int:
        """计算年龄"""
        from datetime import date
        if not birth_date:
            return 0
        today = date.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))