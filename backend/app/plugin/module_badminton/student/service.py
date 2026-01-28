"""

student模块 - Service服务层
"""
from datetime import date, datetime, timedelta
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, ConfigDict

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
from app.core.base_schema import BatchSetAvailable

# ============================================================================
# 临时 Schema 用于处理 out_schema=None 的情况
# ============================================================================

class SimpleOutSchema(BaseModel):
    """简单的输出Schema，只包含id字段"""
    model_config = ConfigDict(from_attributes=True)
    id: int

# ============================================================================
# 学员管理服务
# ============================================================================

class StudentService:
    """学员管理服务层"""

    @classmethod
    async def detail_service(cls, auth: AuthSchema, student_id: int) -> dict:
        """获取学员详情"""
        student = await StudentCRUD(auth).get_by_id_crud(
            id=student_id,
            preload=["parents", "assessments", "created_by", "updated_by"]
        )
        if not student:
            raise CustomException(msg="学员不存在")
        return StudentOutSchema.model_validate(student).model_dump()

    @classmethod
    async def list_service(cls, auth: AuthSchema, search: Optional[StudentQueryParam] = None, order_by: Optional[list[dict[str, str]]] = None) -> list[dict]:
        """学员列表查询"""
        search_dict = search.__dict__ if search else None
        students = await StudentCRUD(auth).list_crud(
            search=search_dict,
            order_by=order_by,
            preload=["parents"]
        )
        return [StudentOutSchema.model_validate(student).model_dump() for student in students]

    @classmethod
    async def page_service(cls, auth: AuthSchema, page_no: int, page_size: int, search: Optional[StudentQueryParam] = None, order_by: Optional[list[dict[str, str]]] = None) -> dict:
        """学员分页查询"""
        if search:
            # 调试：记录search.__dict__的内容
            import json
            from app.core.logger import logger
            logger.debug(f"StudentQueryParam search dict: {search.__dict__}")
        search_dict = search.__dict__ if search else {}
        order_by_list = order_by or [{'id': 'asc'}]
        offset = (page_no - 1) * page_size

        # 不使用 out_schema，直接获取原始对象
        result = await StudentCRUD(auth).page_crud(
            offset=offset,
            limit=page_size,
            order_by=order_by_list,
            search=search_dict,
            preload=["parents"],
            out_schema=None
        )

        # 手动构建返回数据，避免 Pydantic 自动访问懒加载属性
        items = []
        for student in result["items"]:
            item = {
                'id': student.id,
                'uuid': student.uuid,
                'name': student.name,
                'english_name': student.english_name,
                'gender': student.gender.value if student.gender else None,
                'birth_date': student.birth_date.isoformat() if student.birth_date else None,
                'height': student.height,
                'weight': student.weight,
                'handedness': student.handedness.value if student.handedness else None,
                'join_date': student.join_date.isoformat() if student.join_date else None,
                'level': student.level,
                'group_name': student.group_name,
                'campus': student.campus,
                'contact': student.contact,
                'mobile': student.mobile,
                'total_matches': student.total_matches,
                'wins': student.wins,
                'losses': student.losses,
                'win_rate': student.win_rate,
                'status': student.status,
                'created_time': student.created_time.isoformat() if student.created_time else None,
                'updated_time': student.updated_time.isoformat() if student.updated_time else None,
            }
            items.append(item)

        return {
            "total": result["total"],
            "page_no": page_no,
            "page_size": page_size,
            "items": items
        }

    @classmethod
    async def create_service(cls, auth: AuthSchema, data: StudentCreateSchema) -> dict:
        """创建学员"""
        # 检查姓名是否已存在
        existing = await StudentCRUD(auth).get_by_name_crud(data.name)
        if existing:
            raise CustomException(msg="创建失败，学员姓名已存在")
        
        student = await StudentCRUD(auth).create_crud(data=data)
        if not student:
            raise CustomException(msg="创建失败")
        
        return StudentOutSchema.model_validate(student).model_dump()

    @classmethod
    async def update_service(cls, auth: AuthSchema, student_id: int, data: StudentUpdateSchema) -> dict:
        """更新学员"""
        student = await StudentCRUD(auth).get_by_id_crud(student_id)
        if not student:
            raise CustomException(msg="学员不存在")
        
        # 如果修改了姓名，检查是否与其他学员重名
        if data.name and data.name != student.name:
            existing = await StudentCRUD(auth).get_by_name_crud(data.name)
            if existing and existing.id != student_id:
                raise CustomException(msg="更新失败，学员姓名已存在")
        
        updated = await StudentCRUD(auth).update_crud(student_id, data=data)
        if not updated:
            raise CustomException(msg="更新失败")
        
        return StudentOutSchema.model_validate(updated).model_dump()

    @classmethod
    async def delete_service(cls, auth: AuthSchema, student_ids: list[int]) -> dict:
        """删除学员"""
        # 检查学员是否存在且未被使用
        for student_id in student_ids:
            student = await StudentCRUD(auth).get_by_id_crud(student_id)
            if not student:
                raise CustomException(msg=f"学员ID {student_id} 不存在")
            
            # 检查是否有比赛记录
            if student.total_matches > 0:
                raise CustomException(msg=f"学员 {student.name} 有比赛记录，不能删除")
            
            # 检查是否有能力评估记录
            if student.assessments:
                raise CustomException(msg=f"学员 {student.name} 有能力评估记录，不能删除")
        
        await StudentCRUD(auth).delete_crud(student_ids)
        return SimpleResponse(
            success=True,
            message=f"成功删除 {len(student_ids)} 名学员"
        ).model_dump()

    @classmethod
    async def batch_set_status_service(cls, auth: AuthSchema, data: BatchSetAvailable) -> dict:
        """批量设置学员状态"""
        await StudentCRUD(auth).set_available_crud(ids=data.ids, status=data.status)
        return SimpleResponse(
            success=True,
            message=f"成功更新 {len(data.ids)} 名学员状态"
        ).model_dump()

    @classmethod
    async def generate_import_template_service(cls, auth: AuthSchema) -> bytes:
        """生成学员导入Excel模板"""
        try:
            # 表头定义
            headers = [
                "姓名", "英文名", "性别", "出生日期", "身高(cm)", "体重(kg)", 
                "惯用手", "入训日期", "技术水平", "所属组别", "所属校区",
                "紧急联系人", "紧急电话", "备注"
            ]
            
            # 下拉选项表头
            selector_headers = ["性别", "惯用手"]
            
            # 下拉选项配置
            options = [
                {"性别": ["男", "女", "未知"]},
                {"惯用手": ["右手", "左手", "双手"]}
            ]
            
            log.info(f"生成Excel模板，表头: {headers}, 下拉选项: {selector_headers}")
            
            # 验证参数
            if not all(header in headers for header in selector_headers):
                missing = [h for h in selector_headers if h not in headers]
                raise ValueError(f"下拉选项表头不在表头列表中: {missing}")
            
            # 使用ExcelUtil生成模板
            excel_data = ExcelUtil.get_excel_template(
                header_list=headers,
                selector_header_list=selector_headers,
                option_list=options
            )
            
            # 验证返回的数据类型和大小
            if not isinstance(excel_data, bytes):
                error_msg = f"ExcelUtil.get_excel_template返回类型错误: {type(excel_data)}，期望bytes"
                log.error(error_msg)
                raise TypeError(error_msg)
            
            # 检查文件大小和有效性
            if len(excel_data) < 100:  # 正常的Excel文件应该至少有几个KB
                error_msg = f"Excel文件大小异常: {len(excel_data)} bytes，可能不是有效的Excel文件"
                log.error(error_msg)
                raise ValueError(error_msg)
            
            # 检查文件头是否为ZIP格式（Excel文件本质上是ZIP）
            if excel_data[:2] != b'PK':
                error_msg = f"Excel文件头不是ZIP格式(PK开头)，实际: {excel_data[:20].hex()}"
                log.error(error_msg)
                raise ValueError(error_msg)
            
            log.info(f"Excel模板生成成功，文件大小: {len(excel_data)} bytes，文件头验证通过")
            
            # 调试：在开发环境中保存文件以供检查
            import os
            if os.environ.get('ENV') == 'dev' or os.environ.get('FASTAPI_ENV') == 'dev':
                import tempfile
                import uuid
                temp_dir = tempfile.gettempdir()
                filename = f"student_template_debug_{uuid.uuid4().hex[:8]}.xlsx"
                filepath = os.path.join(temp_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(excel_data)
                log.debug(f"调试: Excel模板已保存到 {filepath}")
            
            return excel_data
            
        except Exception as e:
            log.error(f"生成Excel模板失败: {e}", exc_info=True)
            raise CustomException(msg=f"模板生成失败: {str(e)}")

    @classmethod
    async def batch_import_service(cls, auth: AuthSchema, file_content: bytes) -> dict:
        """批量导入学员"""
        from sqlalchemy.exc import SQLAlchemyError
        
        try:
            # 读取Excel文件
            df = pd.read_excel(io.BytesIO(file_content), dtype=str)
            
            # 检查必要的列
            required_columns = ["姓名", "性别", "入训日期"]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise CustomException(msg=f"Excel文件缺少必要列: {', '.join(missing_columns)}")
            
            # 数据验证和导入
            results = {
                "total": len(df),
                "success": 0,
                "failed": 0,
                "errors": []
            }
            
            for idx, row in df.iterrows():
                try:
                    # 跳过空行
                    if pd.isna(row.get("姓名")) or str(row.get("姓名")).strip() == "":
                        continue
                    
                    # 映射字段
                    name = str(row.get("姓名", "")).strip()
                    
                    # 处理日期字段
                    birth_date_str = str(row.get("出生日期", "")).strip() if not pd.isna(row.get("出生日期")) else None
                    birth_date = cls._parse_date(birth_date_str) if birth_date_str else None
                    
                    join_date_str = str(row.get("入训日期", "")).strip()
                    join_date = cls._parse_date(join_date_str) if join_date_str else None
                    
                    # 处理数值字段，处理转换错误
                    height = None
                    height_str = str(row.get("身高(cm)", "")).strip() if not pd.isna(row.get("身高(cm)")) else None
                    if height_str:
                        try:
                            height = float(height_str)
                        except (ValueError, TypeError):
                            height = None
                    
                    weight = None
                    weight_str = str(row.get("体重(kg)", "")).strip() if not pd.isna(row.get("体重(kg)")) else None
                    if weight_str:
                        try:
                            weight = float(weight_str)
                        except (ValueError, TypeError):
                            weight = None
                    
                    student_data = {
                        "name": name,
                        "english_name": str(row.get("英文名", "")).strip() if not pd.isna(row.get("英文名")) else None,
                        "gender": cls._map_gender(str(row.get("性别", "")).strip()),
                        "birth_date": birth_date,
                        "height": height,
                        "weight": weight,
                        "handedness": cls._map_handedness(str(row.get("惯用手", "")).strip()),
                        "join_date": join_date,
                        "level": str(row.get("技术水平", "")).strip() if not pd.isna(row.get("技术水平")) else None,
                        "group_name": str(row.get("所属组别", "")).strip() if not pd.isna(row.get("所属组别")) else None,
                        "campus": str(row.get("所属校区", "")).strip() if not pd.isna(row.get("所属校区")) else None,
                        "emergency_contact": str(row.get("紧急联系人", "")).strip() if not pd.isna(row.get("紧急联系人")) else None,
                        "emergency_phone": str(row.get("紧急电话", "")).strip() if not pd.isna(row.get("紧急电话")) else None,
                        "description": str(row.get("备注", "")).strip() if not pd.isna(row.get("备注")) else None
                    }
                    
                    # 验证和创建学员
                    create_schema = StudentCreateSchema(**student_data)
                    await StudentCRUD(auth).create_crud(data=create_schema)
                    results["success"] += 1
                    
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append({
                        "row": idx + 2,  # Excel行号（第1行是标题）
                        "name": str(row.get("姓名", "")).strip(),
                        "error": str(e)
                    })
                    log.error(f"导入第{idx+2}行失败: {e}")
                    
                    # 如果发生数据库错误，尝试回滚当前事务，以便继续处理后续行
                    if isinstance(e, SQLAlchemyError) and hasattr(auth, 'db'):
                        try:
                            await auth.db.rollback()
                            log.debug(f"已回滚第{idx+2}行的事务")
                        except Exception as rollback_error:
                            log.warning(f"回滚事务失败: {rollback_error}")
            
            return {
                "total": results["total"],
                "success": results["success"],
                "failed": results["failed"],
                "errors": results["errors"]
            }
            
        except Exception as e:
            raise CustomException(msg=f"导入文件处理失败: {str(e)}")

    @staticmethod
    def _map_gender(gender_str: str) -> GenderEnum:
        """映射性别字符串到枚举值"""
        gender_map = {
            "男": GenderEnum.MALE,
            "女": GenderEnum.FEMALE,
            "未知": GenderEnum.UNKNOWN
        }
        return gender_map.get(gender_str, GenderEnum.UNKNOWN)

    @staticmethod
    def _map_handedness(handedness_str: str) -> HandednessEnum:
        """映射惯用手字符串到枚举值"""
        handedness_map = {
            "右手": HandednessEnum.RIGHT,
            "左手": HandednessEnum.LEFT,
            "双手": HandednessEnum.BOTH
        }
        return handedness_map.get(handedness_str, HandednessEnum.RIGHT)

    @staticmethod
    def _parse_date(date_str: str) -> date:
        """解析日期字符串，支持多种格式"""
        if not date_str or date_str.strip() == "":
            raise ValueError("日期字符串不能为空")
        
        date_str = date_str.strip()
        
        # 尝试常见日期格式
        date_formats = [
            "%Y-%m-%d",      # 2023-01-28
            "%Y/%m/%d",      # 2023/01/28
            "%Y.%m.%d",      # 2023.01.28
            "%Y年%m月%d日",   # 2023年01月28日
            "%d/%m/%Y",      # 28/01/2023 (欧洲格式)
            "%m/%d/%Y",      # 01/28/2023 (美国格式)
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        # 如果都失败，尝试使用dateutil.parser（如果可用）
        try:
            from dateutil import parser
            return parser.parse(date_str).date()
        except ImportError:
            pass
        
        # 最后尝试直接使用datetime.fromisoformat（Python 3.7+）
        try:
            return date.fromisoformat(date_str)
        except ValueError:
            pass
        
        raise ValueError(f"无法解析日期字符串: {date_str}，支持的格式: YYYY-MM-DD, YYYY/MM/DD, YYYY.MM.DD等")

# ============================================================================
# 家长-学员关联服务
# ============================================================================

class ParentStudentService:
    """家长-学员关联服务层"""

    @classmethod
    async def create_service(cls, auth: AuthSchema, data: ParentStudentCreateSchema) -> dict:
        """创建家长-学员关联"""
        try:
            relation = await ParentStudentCRUD(auth).create_crud(data=data)
            return ParentStudentOutSchema.model_validate(relation).model_dump()
        except ValueError as e:
            raise CustomException(msg=str(e))

    @classmethod
    async def update_service(cls, auth: AuthSchema, relation_id: int, data: ParentStudentCreateSchema) -> dict:
        """更新关联"""
        relation = await ParentStudentCRUD(auth).update_crud(relation_id, data=data)
        if not relation:
            raise CustomException(msg="关联不存在")
        return ParentStudentOutSchema.model_validate(relation).model_dump()

    @classmethod
    async def delete_service(cls, auth: AuthSchema, relation_ids: list[int]) -> dict:
        """删除关联"""
        await ParentStudentCRUD(auth).delete_crud(relation_ids)
        return SimpleResponse(
            success=True,
            message=f"成功删除 {len(relation_ids)} 个关联"
        ).model_dump()

    @classmethod
    async def get_by_parent_service(cls, auth: AuthSchema, parent_id: int) -> list[dict]:
        """获取家长的所有学员"""
        relations = await ParentStudentCRUD(auth).get_by_parent_id_crud(parent_id)
        return [
            {
                "relation": ParentStudentOutSchema.model_validate(rel).model_dump(),
                "student": StudentOutSchema.model_validate(rel.student).model_dump()
            }
            for rel in relations
        ]

    @classmethod
    async def get_by_student_service(cls, auth: AuthSchema, student_id: int) -> list[dict]:
        """获取学员的所有家长"""
        relations = await ParentStudentCRUD(auth).get_by_student_id_crud(student_id)
        return [ParentStudentOutSchema.model_validate(rel).model_dump() for rel in relations]

# ============================================================================
# 能力评估服务
# ============================================================================

class AbilityAssessmentService:
    """能力评估服务层"""

    @classmethod
    async def create_service(cls, auth: AuthSchema, data: AbilityAssessmentCreateSchema) -> dict:
        """创建能力评估"""
        # 检查学员是否存在
        student = await StudentCRUD(auth).get_by_id_crud(data.student_id)
        if not student:
            raise CustomException(msg="学员不存在")
        
        # 检查评估日期是否已有评估
        existing = await AbilityAssessmentCRUD(auth).get(
            student_id=data.student_id,
            assessment_date=data.assessment_date
        )
        if existing:
            raise CustomException(msg="该学员在指定日期已有评估记录")
        
        assessment = await AbilityAssessmentCRUD(auth).create_crud(data=data)
        return AbilityAssessmentOutSchema.model_validate(assessment).model_dump()

    @classmethod
    async def update_service(cls, auth: AuthSchema, assessment_id: int, data: AbilityAssessmentUpdateSchema) -> dict:
        """更新能力评估"""
        assessment = await AbilityAssessmentCRUD(auth).get_by_id_crud(assessment_id)
        if not assessment:
            raise CustomException(msg="评估记录不存在")
        
        updated = await AbilityAssessmentCRUD(auth).update_crud(assessment_id, data=data)
        return AbilityAssessmentOutSchema.model_validate(updated).model_dump()

    @classmethod
    async def delete_service(cls, auth: AuthSchema, assessment_ids: list[int]) -> dict:
        """删除能力评估"""
        await AbilityAssessmentCRUD(auth).delete_crud(assessment_ids)
        return SimpleResponse(
            success=True,
            message=f"成功删除 {len(assessment_ids)} 条评估记录"
        ).model_dump()

    @classmethod
    async def get_latest_service(cls, auth: AuthSchema, student_id: int) -> Optional[dict]:
        """获取学员最新评估"""
        assessment = await AbilityAssessmentCRUD(auth).get_latest_by_student_crud(student_id)
        if not assessment:
            return None
        return AbilityAssessmentOutSchema.model_validate(assessment).model_dump()

    @classmethod
    async def get_history_service(cls, auth: AuthSchema, student_id: int, limit: int = 10) -> list[dict]:
        """获取学员评估历史"""
        assessments = await AbilityAssessmentCRUD(auth).get_by_student_crud(student_id, limit=limit)
        return [AbilityAssessmentOutSchema.model_validate(ass).model_dump() for ass in assessments]

    @classmethod
    async def list_service(cls, auth: AuthSchema, search: Optional[AbilityAssessmentQueryParam] = None, order_by: Optional[list[dict[str, str]]] = None) -> list[dict]:
        """评估列表查询"""
        search_dict = search.__dict__ if search else None
        assessments = await AbilityAssessmentCRUD(auth).list_crud(
            search=search_dict,
            order_by=order_by,
            preload=["student", "coach", "created_by", "updated_by"]
        )
        return [AbilityAssessmentOutSchema.model_validate(ass).model_dump() for ass in assessments if ass is not None]

    @classmethod
    async def page_service(cls, auth: AuthSchema, page_no: int, page_size: int, search: Optional[AbilityAssessmentQueryParam] = None, order_by: Optional[list[dict[str, str]]] = None) -> dict:
        """评估分页查询"""
        if search:
            search_dict = search.__dict__
        else:
            search_dict = {}
        order_by_list = order_by or [{'id': 'asc'}]
        offset = (page_no - 1) * page_size

        result = await AbilityAssessmentCRUD(auth).page_crud(
            offset=offset,
            limit=page_size,
            order_by=order_by_list,
            search=search_dict,
            preload=["student", "coach", "created_by", "updated_by"],
            out_schema=AbilityAssessmentOutSchema  # 使用out_schema自动处理序列化
        )

        # 确保result不为None
        if result is None:
            result = {"total": 0, "page_no": page_no, "page_size": page_size, "items": []}

        return PaginatedResponse(
            total=result.get("total", 0),
            page_no=result.get("page_no", page_no),
            page_size=result.get("page_size", page_size),
            items=result.get("items", [])
        ).model_dump()
