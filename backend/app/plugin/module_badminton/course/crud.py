"""
course模块 - CRUD数据操作层
"""

from typing import Optional, List, Dict, Any, Sequence

from app.api.v1.module_system.auth.schema import AuthSchema
from app.core.base_crud import CRUDBase
from app.core.database import SessionDep

from .model import *

# ============================================================================
# 课程 CRUD
# ============================================================================

class CourseCRUD(CRUDBase[CourseModel, dict, dict]):
    """课程数据层"""

    def __init__(self, auth: AuthSchema) -> None:
        super().__init__(model=CourseModel, auth=auth)

    async def schedule_crud(self, course_data: dict) -> Optional[CourseModel]:
        """排课"""
        from datetime import datetime
        import logging
        
        logger = logging.getLogger(__name__)
        
        # 记录原始数据
        logger.info(f"📝 开始排课，原始数据: {course_data}")
        
        # 字段映射：CourseCreateSchema -> CourseModel
        mapped_data = {}
        
        # 直接映射的字段
        direct_fields = ["name", "course_type", "coach_id", "max_students", "min_students"]
        for field in direct_fields:
            if field in course_data:
                mapped_data[field] = course_data[field]
                logger.debug(f"📋 直接映射字段 {field}: {course_data[field]}")
        
        # 处理时间字段
        if "start_time" in course_data:
            start_time = course_data["start_time"]
            logger.debug(f"⏰ 处理开始时间: {start_time}")
            if isinstance(start_time, str):
                try:
                    dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    mapped_data["start_date"] = dt.date()
                    mapped_data["class_time"] = dt.time()
                    logger.debug(f"📅 解析开始时间: 日期={dt.date()}, 时间={dt.time()}")
                    
                    # 计算时长（如果有end_time）
                    if "end_time" in course_data:
                        end_time = course_data["end_time"]
                        logger.debug(f"⏰ 处理结束时间: {end_time}")
                        if isinstance(end_time, str):
                            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                            duration_minutes = int((end_dt - dt).total_seconds() / 60)
                            mapped_data["duration_minutes"] = duration_minutes
                            mapped_data["end_date"] = end_dt.date()
                            logger.debug(f"📅 解析结束时间: 日期={end_dt.date()}, 时长={duration_minutes}分钟")
                except (ValueError, AttributeError) as e:
                    logger.error(f"❌ 时间解析失败: {e}")
                    # 如果解析失败，使用默认值
                    mapped_data["start_date"] = datetime.now().date()
                    mapped_data["class_time"] = datetime.now().time()
                    mapped_data["duration_minutes"] = 60
                    logger.warning(f"⚠️ 使用默认时间值")
        
        # 处理地点字段
        if "campus" in course_data and course_data["campus"]:
            mapped_data["location"] = course_data["campus"]
            logger.debug(f"📍 设置校区地点: {course_data['campus']}")
        elif "court_number" in course_data and course_data["court_number"]:
            mapped_data["location"] = course_data["court_number"]
            logger.debug(f"📍 设置场地号: {course_data['court_number']}")
        
        # 处理备注字段
        if "notes" in course_data and course_data["notes"]:
            mapped_data["description"] = course_data["notes"]
            logger.debug(f"📝 设置备注: {course_data['notes']}")
        
        # 设置默认值
        if "duration_minutes" not in mapped_data:
            mapped_data["duration_minutes"] = 60
            logger.debug("⏱️ 设置默认时长: 60分钟")
        if "end_date" not in mapped_data and "start_date" in mapped_data:
            mapped_data["end_date"] = mapped_data["start_date"]
            logger.debug(f"📅 设置结束日期与开始日期相同: {mapped_data['start_date']}")
        if "status" not in mapped_data:
            mapped_data["status"] = "active"
            logger.debug("📊 设置默认状态: active")
        if "current_enrollment" not in mapped_data:
            mapped_data["current_enrollment"] = 0
            logger.debug("👥 设置默认当前报名人数: 0")
        
        logger.info(f"📦 映射后的数据: {mapped_data}")
        
        try:
            # 尝试创建课程
            result = await self.create(data=mapped_data)
            if result:
                logger.info(f"✅ 课程创建成功，ID: {result.id}")
                return result
            else:
                logger.error("❌ 课程创建失败，返回None")
                return None
        except Exception as e:
            logger.error(f"❌ 课程创建异常: {e}", exc_info=True)
            raise

    async def get_upcoming_courses_crud(self, days: int = 7) -> Sequence[CourseModel]:
        """获取近期课程"""
        from datetime import datetime, timedelta
        
        today = datetime.now().date()
        end_date = today + timedelta(days=days)
        
        # 使用日期范围查询 start_date 字段
        return await self.list(
            search={
                "start_date": ("between", (today, end_date))
            },
            order_by=[{"start_date": "asc"}, {"class_time": "asc"}],
            preload=["coach_user"]
        )

    async def page_crud(self, offset: int, limit: int, order_by: list[dict[str, str]], search: dict, out_schema: type, preload: list[str] | None = None) -> dict:
        """课程分页查询"""
        return await self.page(offset=offset, limit=limit, order_by=order_by, search=search, out_schema=out_schema, preload=preload)
