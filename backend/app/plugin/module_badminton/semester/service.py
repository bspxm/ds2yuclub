"""
semester模块 - Service服务层
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
from ..response import SimpleResponse

from app.api.v1.module_system.auth.schema import AuthSchema

# ============================================================================
# 学期管理服务
# ============================================================================

class SemesterService:
    """学期管理服务层"""

    @classmethod
    async def detail_service(cls, auth: AuthSchema, semester_id: int) -> dict:
        """获取学期详情"""
        semester = await SemesterCRUD(auth).get_by_id_crud(
            id=semester_id,
            preload=["created_by", "updated_by"]
        )
        if not semester:
            raise CustomException(msg="学期不存在")
        return SemesterOutSchema.model_validate(semester).model_dump(mode='json')

    @classmethod
    async def list_service(cls, auth: AuthSchema, search: Optional[dict] = None, order_by: Optional[list[dict]] = None) -> list[dict]:
        """学期列表查询"""
        semesters = await SemesterCRUD(auth).list_crud(
            search=search,
            order_by=order_by,
            preload=["created_by"]
        )
        return [SemesterOutSchema.model_validate(semester).model_dump(mode='json') for semester in semesters]

    @classmethod
    async def page_service(cls, auth: AuthSchema, page_no: int, page_size: int, search: Optional[dict | SemesterQueryParam] = None, order_by: Optional[list[dict]] = None) -> dict:
        """学期分页查询"""
        # 将QueryParam对象转换为字典
        if isinstance(search, SemesterQueryParam):
            search_dict = vars(search)
        else:
            search_dict = search or {}

        order_by_list = order_by or [{'id': 'asc'}]
        offset = (page_no - 1) * page_size

        # 不使用 out_schema，直接获取原始对象以避免加载过多关联数据
        result = await SemesterCRUD(auth).page_crud(
            offset=offset,
            limit=page_size,
            order_by=order_by_list,
            search=search_dict,
            preload=["created_by"],
            out_schema=None
        )

        # 手动构建返回数据，只包含必要的字段
        items = []
        for semester in result["items"]:
            item = {
                'id': semester.id,
                'uuid': semester.uuid,
                'name': semester.name,
                'semester_type': semester.semester_type.value if semester.semester_type else None,
                'start_date': semester.start_date.isoformat() if semester.start_date else None,
                'end_date': semester.end_date.isoformat() if semester.end_date else None,
                'week_count': semester.week_count,
                'status': semester.status.value if semester.status else None,
                'is_current': semester.is_current,
                'settlement_date': semester.settlement_date.isoformat() if semester.settlement_date else None,
                'carry_over_enabled': semester.carry_over_enabled,
                'max_carry_over_sessions': semester.max_carry_over_sessions,
                'description': semester.description,
                'status_flag': semester.status_flag,
                'created_time': semester.created_time.isoformat() if semester.created_time else None,
                'updated_time': semester.updated_time.isoformat() if semester.updated_time else None,
            }
            items.append(item)

        return {
            "total": result["total"],
            "page_no": page_no,
            "page_size": page_size,
            "items": items
        }

    @classmethod
    async def create_service(cls, auth: AuthSchema, data: SemesterCreateSchema) -> dict:
        """创建学期"""
        # 检查学期日期是否重叠
        # TODO: 实现日期重叠检查

        semester = await SemesterCRUD(auth).create_crud(data=data)
        if not semester:
            raise CustomException(msg="创建学期失败")
        return SimpleResponse(
            success=True,
            message="学期创建成功",
            data=SemesterOutSchema.model_validate(semester).model_dump(mode='json')
        ).model_dump()

    @classmethod
    async def update_service(cls, auth: AuthSchema, semester_id: int, data: SemesterUpdateSchema) -> dict:
        """更新学期"""
        semester = await SemesterCRUD(auth).update_crud(id=semester_id, data=data)
        if not semester:
            raise CustomException(msg="学期不存在或更新失败")
        return SimpleResponse(
            success=True,
            message="学期更新成功",
            data=SemesterOutSchema.model_validate(semester).model_dump(mode='json')
        ).model_dump()

    @classmethod
    async def delete_service(cls, auth: AuthSchema, semester_ids: list[int]) -> dict:
        """删除学期"""
        await SemesterCRUD(auth).delete_crud(ids=semester_ids)
        return SimpleResponse(
            success=True,
            message="学期删除成功"
        ).model_dump()

    @classmethod
    async def get_current_service(cls, auth: AuthSchema) -> dict:
        """获取当前活跃学期"""
        from datetime import date
        from ..enums import SemesterStatusEnum
        
        # 首先查找进行中的学期
        current_date = date.today()
        
        # 1. 优先查找状态为"进行中"的学期
        active_semesters = await SemesterCRUD(auth).list_crud(
            search={"status": SemesterStatusEnum.ACTIVE},
            order_by=[{"start_date": "desc"}]
        )
        
        if active_semesters:
            # 返回最新的进行中学期
            semester = active_semesters[0]
            return SimpleResponse(
                success=True,
                message="获取当前学期成功",
                data=SemesterOutSchema.model_validate(semester).model_dump(mode='json')
            ).model_dump()
        
        # 2. 如果没有进行中的学期，查找未开始的学期（按开始日期升序，找到即将开始的）
        planning_semesters = await SemesterCRUD(auth).list_crud(
            search={"status": SemesterStatusEnum.PLANNING},
            order_by=[{"start_date": "asc"}]
        )
        
        if planning_semesters:
            # 返回即将开始的学期
            semester = planning_semesters[0]
            return SimpleResponse(
                success=True,
                message="获取即将开始的学期成功",
                data=SemesterOutSchema.model_validate(semester).model_dump(mode='json')
            ).model_dump()
        
        # 3. 如果都没有，返回最近结束的学期
        ended_semesters = await SemesterCRUD(auth).list_crud(
            search={"status": SemesterStatusEnum.ENDED},
            order_by=[{"end_date": "desc"}]
        )
        
        if ended_semesters:
            semester = ended_semesters[0]
            return SimpleResponse(
                success=True,
                message="获取最近结束的学期成功",
                data=SemesterOutSchema.model_validate(semester).model_dump(mode='json')
            ).model_dump()
        
        # 4. 没有任何学期
        raise CustomException(msg="系统中暂无学期信息，请先创建学期")

    @classmethod
    async def close_semester_service(cls, auth: AuthSchema, semester_id: int) -> dict:
        """关闭学期：结算所有购买记录并更新学期状态"""
        from datetime import date
        from ..enums import SemesterStatusEnum
        
        # 获取学期信息
        semester = await SemesterCRUD(auth).get_by_id_crud(id=semester_id)
        if not semester:
            raise CustomException(msg="学期不存在")
        
        # 检查学期是否已结束
        if semester.status == SemesterStatusEnum.COMPLETED:
            raise CustomException(msg="该学期已结束，无需重复操作")
        
        # 1. 结算该学期的所有购买记录
        from .service import PurchaseService
        settlement_result = await PurchaseService.settle_semester_purchases_service(auth, semester_id)
        
        # 2. 更新学期状态为已结束
        updated_semester = await SemesterCRUD(auth).update_crud(
            id=semester_id,
            data={
                "status": SemesterStatusEnum.COMPLETED,
                "end_date": date.today()  # 如果实际结束日期比计划晚，更新为今天
            }
        )
        
        if not updated_semester:
            raise CustomException(msg="更新学期状态失败")
        
        # 3. 生成结转课时报告
        carry_over_report = []
        if settlement_result.get("success") and settlement_result.get("data"):
            settlement_data = settlement_result["data"]
            
            # 分析每个学员的结转课时
            from collections import defaultdict
            student_carry_over = defaultdict(int)
            
            # 这里需要获取实际的购买记录数据来计算每个学员的结转课时
            # 由于settlement_results只包含ID，我们需要查询详细信息
            purchases = await PurchaseCRUD(auth).list_crud(
                search={"semester_id": semester_id, "is_settled": True}
            )
            
            for purchase in purchases:
                if purchase.remaining_sessions > 0:
                    student_carry_over[purchase.student_id] += purchase.remaining_sessions
            
            # 构建结转报告
            for student_id, sessions in student_carry_over.items():
                # 获取学员信息
                from ..student.model import StudentModel
                from app.core.database import async_session
                
                async with async_session() as session:
                    student = await session.get(StudentModel, student_id)
                    if student:
                        carry_over_report.append({
                            "student_id": student_id,
                            "student_name": student.name,
                            "carry_over_sessions": sessions,
                            "note": f"可从学期「{semester.name}」结转{sessions}课时到下个学期"
                        })
        
        return SimpleResponse(
            success=True,
            message=f"学期「{semester.name}」已成功关闭",
            data={
                "semester": SemesterOutSchema.model_validate(updated_semester).model_dump(mode='json'),
                "settlement_summary": settlement_result.get("data", {}),
                "carry_over_report": carry_over_report,
                "next_steps": [
                    "结转课时已记录，学员购买下个学期课程时将自动应用",
                    "教练可以开始为下个学期排课",
                    "家长可以查看学期结算报告"
                ]
            }
        ).model_dump()
