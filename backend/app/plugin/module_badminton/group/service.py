"""
group模块 - Service服务层
"""
from typing import Optional

from pydantic import BaseModel

from sqlalchemy import select, update

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
        """获取分组详情（使用视图优化性能）"""
        import asyncio
        import json
        # 使用视图查询分组信息（已包含教练和学员信息）
        group = await GroupListCRUD(auth).get_by_id_crud(id=group_id)
        if not group:
            raise CustomException(msg="分组不存在")
        
        # 并行查询创建人和更新人
        from app.api.v1.module_system.user.crud import UserCRUD
        related_queries = []
        
        if group.created_id:
            related_queries.append(("creator", UserCRUD(auth).get_by_id_crud(id=group.created_id)))
        
        if group.updated_id:
            related_queries.append(("updater", UserCRUD(auth).get_by_id_crud(id=group.updated_id)))
        
        # 等待查询完成
        related_results = await asyncio.gather(*[r[1] for r in related_queries], return_exceptions=True)
        
        # 提取结果
        created_by = None
        updated_by = None
        for i, (query_name, result) in enumerate(zip([r[0] for r in related_queries], related_results)):
            if isinstance(result, Exception):
                logger.error(f"查询{query_name}信息失败: {result}")
            else:
                if query_name == "creator":
                    created_by = result
                elif query_name == "updater":
                    updated_by = result
        
        # 解析教练列表
        coaches = []
        if group.coaches_json:
            try:
                coaches_data = json.loads(group.coaches_json) if isinstance(group.coaches_json, str) else group.coaches_json
                if isinstance(coaches_data, list):
                    coaches = coaches_data
            except json.JSONDecodeError:
                logger.warning(f"教练信息JSON解析失败")
        
        # 解析学员列表
        students = []
        if group.students_json:
            try:
                students_data = json.loads(group.students_json) if isinstance(group.students_json, str) else group.students_json
                if isinstance(students_data, list):
                    students = students_data
            except json.JSONDecodeError:
                logger.warning(f"学员信息JSON解析失败")
        
        # 处理 datetime 对象
        created_time = group.created_time.isoformat() if group.created_time else None
        updated_time = group.updated_time.isoformat() if group.updated_time else None
        
        created_by_dict = {'id': created_by.id, 'name': created_by.name} if created_by else None
        updated_by_dict = {'id': updated_by.id, 'name': updated_by.name} if updated_by else None
        
        result = {
            'id': group.id,
            'name': group.name,
            'description': group.description,
            'coach_count': group.coach_count if hasattr(group, 'coach_count') else len(coaches),
            'student_count': group.student_count if hasattr(group, 'student_count') else len(students),
            'coaches': coaches,
            'students': students,
            'created_by': created_by_dict,
            'updated_by': updated_by_dict,
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
        """分组分页查询（使用视图优化性能）"""
        search_dict = search.__dict__ if search else {}
        order_by_list = order_by or [{'id': 'asc'}]
        offset = (page_no - 1) * page_size

        # 使用视图模型查询，避免预加载性能问题
        result = await GroupListCRUD(auth).page_crud(
            offset=offset,
            limit=page_size,
            order_by=order_by_list,
            search=search_dict,
            preload=[],  # 视图不需要预加载
            out_schema=None
        )

        # 手动构建返回数据，使用视图的字段
        items = []
        for group in result["items"]:
            # 从 JSON 字段中解析教练和学员列表
            coaches = group.coaches_json if group.coaches_json else []
            students = group.students_json if group.students_json else []

            # 处理 datetime 对象
            created_time = group.created_time.isoformat() if group.created_time else None
            updated_time = group.updated_time.isoformat() if group.updated_time else None

            item = {
                'id': group.id,
                'name': group.name,
                'description': group.description,
                'coach_count': group.coach_count,
                'student_count': group.student_count,
                'coaches': coaches,
                'students': students,
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
        # 查询分组基本信息（不预加载关系）
        from sqlalchemy import select
        async with async_db_session() as db:
            stmt = select(AbilityGroupModel).where(AbilityGroupModel.id == group_id)
            result = await db.execute(stmt)
            group = result.scalar_one_or_none()
        
        if not group:
            raise CustomException(msg="分组不存在")
        
        # 如果修改了名称，检查是否与其他分组重名
        old_name = group.name
        if data.name and data.name != old_name:
            existing = await AbilityGroupCRUD(auth).get_by_name_crud(data.name)
            if existing and existing.id != group_id:
                raise CustomException(msg="更新失败，分组名称已存在")
        
        # 获取原始学员列表（使用 SQL 直接查询，避免预加载）
        from ..student.model import StudentModel
        async with async_db_session() as db:
            stmt = select(StudentModel.id).where(StudentModel.group_name == old_name)
            result = await db.execute(stmt)
            original_student_ids = [row[0] for row in result.all()]
        
        # 更新分组（不预加载关系）
        from ..group.model import GroupCoachModel, GroupStudentModel
        from sqlalchemy import delete
        
        async with async_db_session() as db:
            # 更新分组基本信息
            obj_dict = data.model_dump(exclude_unset=True, exclude={"id", "coach_ids", "student_ids"})
            if obj_dict:
                stmt = (
                    update(AbilityGroupModel)
                    .where(AbilityGroupModel.id == group_id)
                    .values(**obj_dict)
                )
                await db.execute(stmt)
            
            # 处理教练关联
            if data.coach_ids is not None:
                # 删除旧的教练关联
                stmt = delete(GroupCoachModel).where(GroupCoachModel.group_id == group_id)
                await db.execute(stmt)
                # 添加新的教练关联
                if data.coach_ids:
                    db.add_all([GroupCoachModel(group_id=group_id, coach_id=coach_id) for coach_id in data.coach_ids])
            
            # 处理学员关联
            new_student_ids = set(data.student_ids) if data.student_ids is not None else None
            if new_student_ids is not None:
                # 删除旧的学员关联
                stmt = delete(GroupStudentModel).where(GroupStudentModel.group_id == group_id)
                await db.execute(stmt)
                # 添加新的学员关联
                if new_student_ids:
                    db.add_all([GroupStudentModel(group_id=group_id, student_id=student_id) for student_id in new_student_ids])
            
            await db.commit()
        
        # 获取新的分组名称
        new_name = data.name if data.name else old_name
        
        # 批量更新学员的 group_name（合并所有更新操作）
        if new_student_ids is not None:
            old_student_ids_set = set(original_student_ids)
            
            # 新增的学员
            added_students = new_student_ids - old_student_ids_set
            # 移除的学员
            removed_students = old_student_ids_set - new_student_ids
            
            async with async_db_session() as db:
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
        
        # 手动构建返回数据（使用视图查询获取统计信息）
        from .crud import GroupListCRUD
        group_view = await GroupListCRUD(auth).get_by_id_crud(id=group_id)
        
        if group_view:
            return {
                'id': group_view.id,
                'name': group_view.name,
                'description': group_view.description,
                'coach_count': group_view.coach_count,
                'student_count': group_view.student_count,
                'coaches': group_view.coaches_json if group_view.coaches_json else [],
                'students': group_view.students_json if group_view.students_json else [],
                'created_time': group_view.created_time.isoformat() if group_view.created_time else None,
                'updated_time': group_view.updated_time.isoformat() if group_view.updated_time else None
            }
        else:
            return {'id': group_id, 'name': new_name}

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