"""
schedule模块 - Service服务层
"""

import asyncio
import time as time_module
from datetime import date, datetime, timedelta
from typing import Optional, List, Dict, Any
from redis.asyncio.client import Redis
from sqlalchemy.orm import Session

from app.api.v1.module_system.user.service import UserService
from ..student.service import StudentService
from app.core.base_crud import CRUDBase
from app.core.database import SessionDep
from app.core.exceptions import CustomException
from app.core.logger import logger

from .model import *
from .crud import *
from .view_model import ClassScheduleListView
from ..team.schema import (
    ClassScheduleCreateV2Schema,
    ClassScheduleOutSchema,
    ClassScheduleQueryParam,
    AvailableStudentSchema,
    ClassAttendanceCreateSchema,
    ClassAttendanceUpdateSchema
)
from ..purchase.model import PurchaseModel
from ..attendance.model import AttendanceStatusEnum
from ..purchase.crud import PurchaseCRUD
from ..attendance.crud import ClassAttendanceCRUD
from app.common.response import PaginatedResponse
from ..response import SimpleResponse
from app.api.v1.module_system.auth.schema import AuthSchema
from app.api.v1.module_system.dict.service import DictDataService
from ..cache_utils import get_time_slot_dict_with_cache, BadmintonCache, BadmintonCacheKeys, CacheExpireTime

# ============================================================================
# 羽毛球时间段代码映射（支持扩展到J，无数量限制）
# 格式：{day_index}{slot_code}，例如：0A, 6A, 6J
# ============================================================================

# ============================================================================
# 排课记录管理服务
# ============================================================================

class ClassScheduleService:
    """排课记录管理服务层"""

    @classmethod
    async def detail_service(cls, auth: AuthSchema, redis: Redis, schedule_id: int) -> dict:
        """获取排课记录详情（优化版：使用视图获取排课、班级、教练信息 + 并行查询其他数据 + Redis缓存）"""
        import time as time_module
        logger.info(f"获取排课记录详情，schedule_id={schedule_id}")

        total_start = time_module.time()

        # 尝试从Redis缓存获取
        cache_key = f"{BadmintonCacheKeys.CLASS_SCHEDULE_DETAIL}:{schedule_id}"
        cache_start = time_module.time()
        try:
            cached_result = await BadmintonCache.get_json(redis, cache_key)
            cache_end = time_module.time()
            if cached_result is not None:
                logger.info(f"从缓存获取排课详情: schedule_id={schedule_id}, 缓存耗时: {cache_end - cache_start:.3f}秒")
                return cached_result
        except Exception as e:
            cache_end = time_module.time()
            logger.warning(f"获取缓存失败: schedule_id={schedule_id}, error={e}")

        # 1. 使用视图查询排课记录（已包含班级和教练信息）
        schedule_start = time_module.time()
        from .crud import ClassScheduleListCRUD
        schedule = await ClassScheduleListCRUD(auth).get_by_id_crud(id=schedule_id)
        schedule_end = time_module.time()
        logger.info(f"查询排课记录（使用视图）耗时: {schedule_end - schedule_start:.3f}秒")

        if not schedule:
            raise CustomException(msg="排课记录不存在")

        # 2. 并行查询其他关联数据（创建人、更新人、考勤记录）
        from app.api.v1.module_system.user.crud import UserCRUD
        from app.plugin.module_badminton.attendance.crud import ClassAttendanceCRUD

        # 并行查询创建人、更新人、考勤记录
        related_queries = []

        if schedule.created_id:
            related_queries.append(("creator", UserCRUD(auth).get_by_id_crud(id=schedule.created_id)))

        if schedule.updated_id:
            related_queries.append(("updater", UserCRUD(auth).get_by_id_crud(id=schedule.updated_id)))

        # 查询考勤记录（只获取 student_id，不预加载关联数据）
        related_queries.append(("attendance", ClassAttendanceCRUD(auth).list_crud(
            search={"schedule_id": ("eq", schedule_id)},
            preload=[]  # 不预加载任何关联数据，只需要 student_id
        )))

        # 等待所有查询完成
        related_start = time_module.time()
        related_results = await asyncio.gather(*[r[1] for r in related_queries], return_exceptions=True)
        related_end = time_module.time()
        logger.info(f"并行查询其他关联数据耗时: {related_end - related_start:.3f}秒，查询数: {len(related_queries)}")

        # 提取结果并处理异常
        created_by = None
        updated_by = None
        attendance_records = []

        for i, (query_name, result) in enumerate(zip([r[0] for r in related_queries], related_results)):
            if isinstance(result, Exception):
                logger.error(f"查询{query_name}信息失败: {result}")
            else:
                logger.info(f"查询{query_name}成功")
                if query_name == "creator":
                    created_by = result
                elif query_name == "updater":
                    updated_by = result
                elif query_name == "attendance":
                    attendance_records = result if result else []

        # 构建返回数据
        data = ClassScheduleOutSchema.model_validate(schedule).model_dump()

        # 从视图中获取的班级和教练信息
        data['semester_id'] = schedule.class_ref_semester_id if schedule.class_ref_semester_id else None
        data['class'] = {"id": schedule.class_ref_id, "name": schedule.class_ref_name} if schedule.class_ref_id else None
        data['coach'] = {"id": schedule.coach_user_id, "name": schedule.coach_user_name} if schedule.coach_user_id else None

        # 添加创建人和更新人信息
        if created_by:
            data['created_by'] = {"id": created_by.id, "name": created_by.name}

        if updated_by:
            data['updated_by'] = {"id": updated_by.id, "name": updated_by.name}

        # 添加学员ID列表（从考勤记录中提取）
        if attendance_records:
            student_ids = [att.student_id for att in attendance_records if att.student_id]
            data['student_ids'] = student_ids
            logger.info(f"从考勤记录中提取学员IDs: {student_ids}")
        else:
            data['student_ids'] = []
            logger.info(f"没有考勤记录，student_ids=[]")

        # 存入Redis缓存（缓存5分钟）
        try:
            await BadmintonCache.set_json(redis, cache_key, data, 300)
            logger.info(f"排课详情已缓存: schedule_id={schedule_id}")
        except Exception as e:
            logger.warning(f"缓存写入失败: schedule_id={schedule_id}, error={e}")

        total_end = time_module.time()
        logger.info(f"detail_service 总耗时: {total_end - total_start:.3f}秒")

        return data
    @classmethod
    async def list_service(cls, auth: AuthSchema, search: Optional[dict] = None, order_by: Optional[list[dict]] = None) -> list[dict]:
        """排课记录列表查询"""
        schedules = await ClassScheduleCRUD(auth).list_crud(
            search=search,
            order_by=order_by,
            preload=["class_ref", "coach_user"]
        )
        return [ClassScheduleOutSchema.model_validate(schedule).model_dump() for schedule in schedules]

    @classmethod
    async def page_service(cls, auth: AuthSchema, page_no: int, page_size: int, search: Optional[dict | ClassScheduleQueryParam] = None, order_by: Optional[list[dict]] = None) -> dict:
        """排课记录分页查询（使用视图优化性能）"""
        import time as time_module
        total_start = time_module.time()
        
        # 显式导入需要的模型，避免循环导入问题
        from ..attendance.model import ClassAttendanceModel
        from .view_model import ClassScheduleListView
        
        # 将QueryParam对象转换为字典
        if isinstance(search, ClassScheduleQueryParam):
            search_dict = vars(search)
        else:
            search_dict = search or {}

        order_by_list = order_by or [{'id': 'asc'}]
        offset = (page_no - 1) * page_size

        # 使用视图模型查询，避免预加载性能问题
        # 视图已经包含了班级和教练信息，不需要预加载
        page_start = time_module.time()
        from .crud import ClassScheduleListCRUD
        result = await ClassScheduleListCRUD(auth).page_crud(
            offset=offset,
            limit=page_size,
            order_by=order_by_list,
            search=search_dict,
            preload=[],  # 视图不需要预加载
            out_schema=None
        )
        page_end = time_module.time()
        logger.info(f"排课记录分页查询耗时（使用视图）: {page_end - page_start:.3f}秒, 结果数: {len(result['items'])}")

        # 批量查询学员数（使用子查询，避免N+1问题）
        from sqlalchemy import select, func
        schedule_ids = [s.id for s in result["items"]]
        student_counts = {}
        
        student_count_start = time_module.time()
        if schedule_ids:
            # 使用子查询统计每个排课的学员数
            student_count_query = (
                select(
                    ClassAttendanceModel.schedule_id,
                    func.count(ClassAttendanceModel.id).label('count')
                )
                .where(ClassAttendanceModel.schedule_id.in_(schedule_ids))
                .group_by(ClassAttendanceModel.schedule_id)
            )
            count_result = await auth.db.execute(student_count_query)
            for row in count_result:
                student_counts[row.schedule_id] = row.count
        
        student_count_end = time_module.time()
        logger.info(f"学员数统计查询耗时: {student_count_end - student_count_start:.3f}秒")

        # 手动构建返回数据，使用视图的字段
        items = []
        for schedule in result["items"]:
            # 使用批量查询的学员数
            student_count = student_counts.get(schedule.id, 0)
            
            item = {
                'id': schedule.id,
                'uuid': schedule.uuid,
                'class_id': schedule.class_id,
                'schedule_date': schedule.schedule_date.isoformat() if schedule.schedule_date else None,
                'day_of_week': schedule.day_of_week,
                'time_slot_code': schedule.time_slot_code,
                'time_slots_json': schedule.time_slots_json,
                'start_time': schedule.start_time.isoformat() if schedule.start_time else None,
                'end_time': schedule.end_time.isoformat() if schedule.end_time else None,
                'duration_minutes': schedule.duration_minutes,
                'schedule_type': schedule.schedule_type,
                'schedule_status': schedule.schedule_status,
                'coach_id': schedule.coach_id,
                'coach_confirmed': schedule.coach_confirmed,
                'coach_confirm_at': schedule.coach_confirm_at.isoformat() if schedule.coach_confirm_at else None,
                'court_number': schedule.court_number,
                'location': schedule.location,
                'topic': schedule.topic,
                'content_summary': schedule.content_summary,
                'training_focus': schedule.training_focus,
                'equipment_needed': schedule.equipment_needed,
                'is_published': schedule.is_published,
                'published_at': schedule.published_at.isoformat() if schedule.published_at else None,
                'is_auto_generated': schedule.is_auto_generated,
                'original_schedule_id': schedule.original_schedule_id,
                'makeup_for_schedule_id': schedule.makeup_for_schedule_id,
                'notes': schedule.notes,
                'status': schedule.status,
                'created_time': schedule.created_time.isoformat() if schedule.created_time else None,
                'updated_time': schedule.updated_time.isoformat() if schedule.updated_time else None,
                'student_count': student_count,
                # 关联对象（使用视图字段）
                'class': {
                    'id': schedule.class_ref_id,
                    'name': schedule.class_ref_name,
                    'semester_id': schedule.class_ref_semester_id
                } if schedule.class_ref_id else None,
                'coach': {
                    'id': schedule.coach_user_id,
                    'name': schedule.coach_user_name
                } if schedule.coach_user_id else None,
            }
            items.append(item)

        total_end = time_module.time()
        logger.info(f"排课记录列表查询总耗时: {total_end - total_start:.3f}秒")

        return {
            "total": result["total"],
            "page_no": page_no,
            "page_size": page_size,
            "items": items
        }

    @classmethod
    async def update_service(cls, auth: AuthSchema, redis: Redis, schedule_id: int, data: ClassScheduleCreateV2Schema) -> dict:
        """更新排课记录"""
        # 转换数据为字典
        data_dict = data.model_dump(exclude_unset=True)
        
        # 添加调试日志
        logger.info(f"更新排课记录 ID={schedule_id}, 原始数据: {data_dict}")
        
        # 处理日期字段：将字符串转换为 date 对象
        if "schedule_date" in data_dict and isinstance(data_dict["schedule_date"], str):
            from datetime import datetime
            data_dict["schedule_date"] = datetime.strptime(data_dict["schedule_date"], "%Y-%m-%d").date()

        # 保存时间段字典数据（用于后续创建考勤记录时传递，避免重复查询Redis）
        cached_time_slot_data = None

        # 如果提供了 time_slots_json，填充时间字段
        if "time_slots_json" in data_dict and data_dict["time_slots_json"]:
            # 从Redis获取羽毛球时间段字典
            cached_time_slot_data = await DictDataService.get_init_dict_service(
                redis=redis,
                dict_type='badminton_time_slot'
            )

            # 解析 time_slots_json
            try:
                time_slots = json.loads(data_dict["time_slots_json"])
            except json.JSONDecodeError:
                logger.warning(f"时间段配置格式错误: {data_dict['time_slots_json']}")
                time_slots = {}

            # 获取第一个时间段（排课记录只包含一个时间段）
            if time_slots:
                day_name, slot_codes = list(time_slots.items())[0]
                slot_code = slot_codes[0] if slot_codes else ''

                if slot_code:
                    # 从字典中查找时间段信息
                    time_slot_info = None
                    for slot in cached_time_slot_data:
                        if slot.get('dict_value') == slot_code:
                            time_slot_info = slot
                            break

                    if time_slot_info:
                        # 解析时间范围
                        dict_label = time_slot_info.get('dict_label', '')
                        if '-' in dict_label:
                            time_parts = dict_label.split('-')
                            start_time_str = time_parts[0].strip()
                            end_time_str = time_parts[1].strip()
                        else:
                            start_time_str = '08:00'
                            end_time_str = '09:30'

                        # 填充时间字段
                        if "start_time" not in data_dict or data_dict["start_time"] is None:
                            data_dict["start_time"] = datetime.strptime(start_time_str, '%H:%M').time()
                        if "end_time" not in data_dict or data_dict["end_time"] is None:
                            data_dict["end_time"] = datetime.strptime(end_time_str, '%H:%M').time()
                        if "duration_minutes" not in data_dict or data_dict["duration_minutes"] is None:
                            data_dict["duration_minutes"] = 90

        # 提取学员列表（如果有值则更新）
        student_ids = data_dict.pop("student_ids", None)
        logger.info(f"更新排课记录 ID={schedule_id}, 学员IDs: {student_ids}")
        
        # 将转换后的数据传递给 CRUD
        schedule = await ClassScheduleCRUD(auth).update_crud(id=schedule_id, data=data_dict)
        if not schedule:
            raise CustomException(msg="排课记录不存在或更新失败")
        
        # 如果提供了学员列表，则更新考勤记录
        if student_ids is not None:
            try:
                # 直接删除旧的考勤记录（使用原生SQL，提高性能）
                from app.plugin.module_badminton.attendance.model import ClassAttendanceModel
                from sqlalchemy import delete as sql_delete
                
                # 记录开始时间
                delete_start = time_module.time()
                
                # 直接执行DELETE语句
                delete_stmt = sql_delete(ClassAttendanceModel).where(ClassAttendanceModel.schedule_id == schedule_id)
                await auth.db.execute(delete_stmt)
                await auth.db.flush()
                
                delete_end = time_module.time()
                logger.info(f"排课ID={schedule_id}：删除旧考勤记录完成，耗时: {delete_end - delete_start:.3f}秒")
                
                # 2. 为新的学员列表创建考勤记录
                if student_ids and len(student_ids) > 0:
                    created_count = await cls.auto_create_attendance_service(
                        auth=auth,
                        redis=redis,
                        schedule_id=schedule_id,
                        student_ids=student_ids,
                        time_slot_data=cached_time_slot_data  # 传递缓存的时间段字典
                    )
                    logger.info(f"排课ID={schedule_id}：创建新考勤记录 {created_count}/{len(student_ids)}")
            except Exception as e:
                logger.error(f"排课ID={schedule_id}：更新考勤记录失败：{str(e)}")
                # 考勤更新失败不影响排课记录更新
        
        return SimpleResponse(
            success=True,
            message="排课记录更新成功",
            data=ClassScheduleOutSchema.model_validate(schedule).model_dump()
        ).model_dump()

    @classmethod
    async def delete_service(cls, auth: AuthSchema, schedule_ids: list[int]) -> dict:
        """删除排课记录"""
        await ClassScheduleCRUD(auth).delete_crud(ids=schedule_ids)
        return SimpleResponse(
            success=True,
            message="排课记录删除成功"
        ).model_dump()

    @classmethod
    async def auto_reschedule_for_leave(cls, auth: AuthSchema, schedule_id: int, student_id: int) -> dict:
        """
        请假自动顺延：当学员请假时，自动预约下周同一时间的补课

        Args:
            auth: 认证信息
            schedule_id: 原排课记录ID
            student_id: 请假学员ID

        Returns:
            dict: 新的排课记录信息
        """
        # 获取原排课记录
        original_schedule = await ClassScheduleCRUD(auth).get_by_id_crud(
            id=schedule_id,
            preload=["class_ref"]
        )
        if not original_schedule:
            raise CustomException(msg="原排课记录不存在")

        # 计算下周同一时间
        if original_schedule.schedule_date:
            original_date = original_schedule.schedule_date
            next_week_date = original_date + timedelta(days=7)

            # 准备时间段配置（使用 time_slots_json）
            time_slots = {}
            if original_schedule.time_slots_json:
                time_slots = json.loads(original_schedule.time_slots_json)

            # 创建新的排课记录（补课）
            new_schedule_data = ClassScheduleCreateV2Schema(
                semester_id=original_schedule.class_ref.semester_id if original_schedule.class_ref else 1,
                schedule_date=next_week_date,
                class_ids=[original_schedule.class_id],
                coach_id=original_schedule.coach_id,
                time_slots=time_slots,
                schedule_status=ScheduleStatusEnum.SCHEDULED,
                schedule_type=ScheduleTypeEnum.MAKEUP,
                student_ids=[student_id],
                notes=f"学员ID:{student_id}请假自动顺延补课"
            )

            new_schedule = await ClassScheduleCRUD(auth).create_crud(data=new_schedule_data)
            if not new_schedule:
                raise CustomException(msg="创建补课排课记录失败")

            logger.info(f"学员{student_id}请假，已自动创建补课排课记录：{new_schedule.id}")

            return SimpleResponse(
                success=True,
                message="请假自动顺延补课已安排",
                data=ClassScheduleOutSchema.model_validate(new_schedule).model_dump()
            ).model_dump()
        else:
            raise CustomException(msg="原排课记录缺少日期或时间信息")

    @classmethod
    async def get_available_students_service(cls, auth: AuthSchema, redis: Redis, semester_id: int,
                                           schedule_date: date, time_slots: dict[str, list[str]], 
                                           class_ids: list[int] | None = None) -> list[dict]:
        """
        获取可用学员列表

        筛选逻辑：
        1. 查询指定班级（如果未提供则查询该学期下所有班级）
        2. 查询这些班级的购买记录
        3. 筛选 selected_time_slots 包含任一时间段代码的购买记录
        4. 检查学员是否有剩余课时
        5. 检查排课日期是否在购买记录的有效期内
        6. 返回符合条件的学员列表

        Args:
            auth: 认证信息
            semester_id: 学期ID
            schedule_date: 排课日期
            time_slots: 时间段配置（格式：{"周一": ["A", "B"], "周三": ["C"]}）
            class_ids: 班级ID列表（可选，如果未提供则查询该学期下所有班级）

        Returns:
            list[dict]: 可用学员列表
        """
        import json
        from app.plugin.module_badminton.team.crud import ClassCRUD
        from app.plugin.module_badminton.purchase.crud import PurchaseCRUD

        # 尝试从Redis缓存获取
        time_slots_hash = BadmintonCache.hash_dict(time_slots)
        class_ids_str = ",".join(map(str, sorted(class_ids))) if class_ids else "all"
        cache_key = f"{BadmintonCacheKeys.AVAILABLE_STUDENTS}:{semester_id}:{schedule_date}:{time_slots_hash}:{class_ids_str}"

        try:
            cached_result = await BadmintonCache.get_json(redis, cache_key)
            if cached_result is not None:
                logger.info(f"从缓存获取可用学员列表: semester_id={semester_id}, date={schedule_date}, 学员数={len(cached_result) if isinstance(cached_result, list) else 'N/A'}")
                return cached_result
        except Exception as e:
            logger.warning(f"获取缓存失败，将继续查询数据库: key={cache_key}, error={e}")

        # 1. 查询班级（使用视图优化）
        from ..team.crud import ClassListCRUD
        class_query_start = time_module.time()
        if class_ids and len(class_ids) > 0:
            # 查询指定班级（使用视图）
            classes = await ClassListCRUD(auth).list_crud(
                search={"id": ("in", class_ids)}
            )
        else:
            # 查询该学期下所有班级（使用视图）
            classes = await ClassListCRUD(auth).list_crud(
                search={"semester_id": ("eq", semester_id)}
            )
        class_query_end = time_module.time()
        logger.info(f"查询班级耗时（使用视图）: {class_query_end - class_query_start:.3f}秒, 班级数: {len(classes)}")
        
        if not classes:
            return []

        target_class_ids = [c.id for c in classes]

        # 2. 查询这些班级的购买记录（使用视图优化）
        from ..purchase.crud import PurchaseListCRUD
        purchase_query_start = time_module.time()
        purchases = await PurchaseListCRUD(auth).list_crud(
            search={"class_id": ("in", target_class_ids)}
        )
        purchase_query_end = time_module.time()
        logger.info(f"查询购买记录耗时（使用视图）: {purchase_query_end - purchase_query_start:.3f}秒, 购买记录数: {len(purchases)}")
        if not purchases:
            return []

        # 3. 批量查询学员信息（使用学员视图，提高性能）
        student_query_start = time_module.time()
        student_ids = list(set([p.student_id for p in purchases if p.student_id]))
        students_map = {}
        if student_ids:
            from app.plugin.module_badminton.student.crud import StudentListCRUD
            students = await StudentListCRUD(auth).list_crud(
                search={"id": ("in", student_ids)}
            )
            students_map = {s.id: s for s in students}
        student_query_end = time_module.time()
        logger.info(f"查询学员信息耗时: {student_query_end - student_query_start:.3f}秒, 学员数: {len(students_map)}")

        available_students = []
        day_names = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
        day_of_week = schedule_date.weekday()  # 0=周一, 6=周日
        # 转换为中文星期名称
        day_name = day_names[day_of_week]

        # time_slots 已经是 JSON 格式: {'周一': ['A', 'B'], '周二': ['C']}
        target_slots = time_slots

        filter_start = time_module.time()
        for purchase in purchases:
            # 3. 筛选 selected_time_slots 包含任一时间段代码的购买记录
            if not purchase.selected_time_slots:
                continue

            try:
                selected_slots = json.loads(purchase.selected_time_slots)
            except json.JSONDecodeError:
                continue

            # 检查是否有任一时间段在购买记录的时间段配置中
            # 逻辑：检查学员购买的时间段中，是否包含任一目标时间段
            has_matching_slot = False
            for target_day, target_codes in target_slots.items():
                if target_day in selected_slots:
                    student_codes = selected_slots[target_day]
                    if any(code in student_codes for code in target_codes):
                        has_matching_slot = True
                        break

            # 从批量查询的学员信息中获取学员
            student = students_map.get(purchase.student_id)
            if not student:
                continue

            # 添加调试日志
            logger.info(f"检查学员: {student.name}, 购买记录selected_time_slots: {selected_slots}, 目标时间段: {target_slots}, 匹配: {has_matching_slot}, 剩余课时: {purchase.remaining_sessions}, 有效期: {purchase.valid_from} ~ {purchase.valid_until}")

            if not has_matching_slot:
                continue

            # 4. 检查学员是否有剩余课时
            if purchase.remaining_sessions <= 0:
                logger.info(f"学员 {student.name} 剩余课时不足: {purchase.remaining_sessions}")
                continue

            # 5. 检查排课日期是否在购买记录的有效期内
            if not (purchase.valid_from <= schedule_date <= purchase.valid_until):
                logger.info(f"学员 {student.name} 排课日期不在有效期内: {schedule_date} 不在 {purchase.valid_from} ~ {purchase.valid_until} 之间")
                continue

            # 添加到可用学员列表
            available_students.append(AvailableStudentSchema(
                id=student.id,
                uuid=student.uuid,
                name=student.name,
                student_name=student.name,  # 添加别名字段，用于前端显示
                english_name=student.english_name,
                gender=student.gender.value if student.gender else None,
                birth_date=student.birth_date.isoformat() if student.birth_date else None,
                level=student.level,
                group_name=student.group_name,
                total_sessions=purchase.total_sessions,
                used_sessions=purchase.used_sessions,
                remaining_sessions=purchase.remaining_sessions,
                purchase_id=purchase.id,
                valid_from=purchase.valid_from.isoformat(),
                valid_until=purchase.valid_until.isoformat()
            ).model_dump())

        filter_end = time_module.time()
        logger.info(f"筛选逻辑耗时: {filter_end - filter_start:.3f}秒, 检查了 {len(purchases)} 条购买记录, 筛选出 {len(available_students)} 名学员")

        logger.info(f"获取可用学员列表：学期ID={semester_id}, 日期={schedule_date}, 时间段={time_slots}, 班级ID={class_ids if class_ids else '全部'}, 学员数={len(available_students)}")

        # 存入Redis缓存
        try:
            await BadmintonCache.set_json(redis, cache_key, available_students, CacheExpireTime.AVAILABLE_STUDENTS)
            logger.info(f"可用学员列表已缓存: semester_id={semester_id}, date={schedule_date}")
        except Exception as e:
            logger.warning(f"缓存设置失败: key={cache_key}, error={e}")

        return available_students

    @classmethod
    async def auto_create_attendance_service(cls, auth: AuthSchema, redis: Redis, schedule_id: int,
                                           student_ids: list[int], time_slot_data: list[dict] | None = None) -> int:
        """
        为排课记录自动创建考勤记录

        逻辑：
        1. 获取排课记录信息
        2. 从 time_slots_json 解析时间段信息
        3. 为每个学员查找对应的购买记录
        4. 创建考勤记录（默认状态：PRESENT）
        5. 自动扣减课时

         Args:
             auth: 认证信息
             redis: Redis客户端
             schedule_id: 排课记录ID
             student_ids: 学员ID列表
             time_slot_data: 可选的时间段字典数据（避免重复查询Redis）

        Returns:
            int: 创建的考勤记录数量
         """
        import json
        from datetime import time
        from sqlalchemy import select, and_
        
        # 1. 获取排课记录
        schedule = await ClassScheduleCRUD(auth).get_by_id_crud(
            id=schedule_id,
            preload=["class_ref"]
        )
        if not schedule:
            raise CustomException(msg="排课记录不存在")

        # 2. 检查 schedule.start_time, end_time, duration_minutes 是否已经设置
        if schedule.start_time and schedule.end_time and schedule.duration_minutes:
            start_time = schedule.start_time
            end_time = schedule.end_time
            duration_minutes = schedule.duration_minutes
        else:
            # 从 time_slots_json 解析时间段信息
            if not schedule.time_slots_json:
                raise CustomException(msg="排课记录缺少时间段配置")
            
            try:
                time_slots = json.loads(schedule.time_slots_json)
            except json.JSONDecodeError:
                raise CustomException(msg="时间段配置格式错误")
            
            # 获取第一个时间段（排课记录只包含一个时间段）
            if not time_slots:
                raise CustomException(msg="时间段配置为空")
            
            # 获取第一个星期和时间段代码
            day_name, slot_codes = list(time_slots.items())[0]
            slot_code = slot_codes[0] if slot_codes else ''
            
            if not slot_code:
                raise CustomException(msg="时间段配置无效")

            # 优先使用传入的时间段字典，避免重复查询Redis
            if time_slot_data is None:
                time_slot_data = await DictDataService.get_init_dict_service(
                    redis=redis,
                    dict_type='badminton_time_slot'
                )

            # 从字典中查找时间段信息
            time_slot_info = None
            for slot in time_slot_data:
                if slot.get('dict_value') == slot_code:
                    time_slot_info = slot
                    break

            if not time_slot_info:
                raise CustomException(msg=f"时间段代码 {slot_code} 在字典中不存在")

            # 解析时间范围
            dict_label = time_slot_info.get('dict_label', '')
            if '-' in dict_label:
                time_parts = dict_label.split('-')
                start_time_str = time_parts[0].strip()
                end_time_str = time_parts[1].strip()
            else:
                start_time_str = '08:00'
                end_time_str = '09:30'

            # 转换为time对象
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
            duration_minutes = 90
        
        created_count = 0

        # 3. 批量查询所有学员的购买记录（减少数据库查询次数）
        from app.plugin.module_badminton.purchase.model import PurchaseModel
        from sqlalchemy import select, and_
        
        purchase_start = time_module.time()
        
        # 一次性查询所有学员的购买记录
        purchase_query = select(PurchaseModel).where(
            and_(
                PurchaseModel.student_id.in_(student_ids),
                PurchaseModel.class_id == schedule.class_id,
                PurchaseModel.remaining_sessions > 0
            )
        ).order_by(PurchaseModel.created_time.desc())
        
        purchase_result = await auth.db.execute(purchase_query)
        all_purchases = purchase_result.scalars().all()
        
        purchase_end = time_module.time()
        logger.info(f"批量查询购买记录完成：学员数={len(student_ids)}, 查到购买记录数={len(all_purchases)}, 耗时: {purchase_end - purchase_start:.3f}秒")
        
        # 按学员ID分组购买记录
        student_purchases = {}
        for purchase in all_purchases:
            if purchase.student_id not in student_purchases:
                student_purchases[purchase.student_id] = []
            student_purchases[purchase.student_id].append(purchase)
        
        # 准备批量创建考勤记录和批量扣减课时
        attendance_records = []
        purchase_updates = {}
        
        for student_id in student_ids:
            # 获取该学员的购买记录
            purchases = student_purchases.get(student_id, [])
            
            if not purchases:
                logger.warning(f"学员{student_id}没有购买班级{schedule.class_id}的课时包")
                continue
            
            # 使用最近购买的课时包
            purchase = purchases[0]
            
            # 检查是否有剩余课时
            if purchase.remaining_sessions <= 0:
                logger.warning(f"学员{student_id}的课时包{purchase.id}没有剩余课时")
                continue
            
            # 准备考勤记录数据
            attendance_records.append({
                "student_id": student_id,
                "class_id": schedule.class_id,
                "schedule_id": schedule_id,
                "purchase_id": purchase.id,
                "attendance_date": schedule.schedule_date,
                "start_time": start_time,
                "end_time": end_time,
                "duration_minutes": duration_minutes,
                "attendance_status": AttendanceStatusEnum.PRESENT,
                "session_deducted": 1,
                "is_auto_deduct": True,
                "coach_id": schedule.coach_id
            })
            
            # 准备课时扣减
            if purchase.id not in purchase_updates:
                purchase_updates[purchase.id] = {
                    "used_sessions": purchase.used_sessions + 1,
                    "remaining_sessions": purchase.remaining_sessions - 1
                }
        
        # 批量创建考勤记录 - 使用原生SQL批量插入
        create_start = time_module.time()
        if attendance_records:
            from sqlalchemy import insert as sql_insert
            from app.plugin.module_badminton.attendance.model import ClassAttendanceModel
            
            try:
                # 使用批量插入
                insert_stmt = sql_insert(ClassAttendanceModel).values(attendance_records)
                result = await db.execute(insert_stmt)
                await db.flush()
                
                created_count = result.rowcount
                logger.info(f"批量创建考勤记录成功：准备={len(attendance_records)}, 成功={created_count}, 耗时: {create_end - create_start:.3f}秒")
            except Exception as e:
                logger.error(f"批量创建考勤记录失败：{e}")
                # 如果批量插入失败，降级为逐个插入
                for attendance_data in attendance_records:
                    try:
                        attendance = await ClassAttendanceCRUD(auth).create_crud(data=attendance_data)
                        if attendance:
                            created_count += 1
                    except Exception as err:
                        logger.error(f"创建考勤记录失败（降级模式）：{err}")
        
        create_end = time_module.time()
        logger.info(f"批量创建考勤记录完成：准备={len(attendance_records)}, 成功={created_count}, 耗时: {create_end - create_start:.3f}秒")
        
        # 批量扣减课时 - 使用原生SQL批量更新
        update_start = time_module.time()
        if purchase_updates:
            for purchase_id, update_data in purchase_updates.items():
                update_stmt = sql_update(PurchaseModel).where(PurchaseModel.id == purchase_id).values(**update_data)
                await db.execute(update_stmt)
            
            await db.flush()
            
            for purchase_id in purchase_updates.keys():
                logger.info(f"扣减课时成功：购买记录ID={purchase_id}")
        
        update_end = time_module.time()
        logger.info(f"批量扣减课时完成：数量={len(purchase_updates)}, 耗时: {update_end - update_start:.3f}秒")

        logger.info(f"自动创建考勤记录完成：排课ID={schedule_id}, 学员数={len(student_ids)}, 成功={created_count}")

        return created_count

    @classmethod
    async def create_v2_service(cls, auth: AuthSchema, redis: Redis, data: ClassScheduleCreateV2Schema) -> dict:
        """
        创建排课记录（V2版本）- 支持学员选择和自动创建考勤，支持时间段多选
        
        流程：
        1. 验证数据（学期、班级、教练、日期）
        2. 为每个时间段创建一条排课记录
        3. 为每个排课记录自动为选中的学员创建考勤记录
        4. 返回所有创建的排课记录
        
        Args:
            auth: 认证信息
            redis: Redis客户端
            data: 排课创建数据（V2版本）
        
        Returns:
            dict: 创建结果
        """
        from app.plugin.module_badminton.semester.crud import SemesterCRUD
        from app.plugin.module_badminton.team.crud import ClassCRUD
        from datetime import datetime
        import json

        # 1. 验证学期
        semester = await SemesterCRUD(auth).get_by_id_crud(id=data.semester_id)
        if not semester:
            raise CustomException(msg="学期不存在")

        # 验证排课日期是否在学期范围内
        if not (semester.start_date <= data.schedule_date <= semester.end_date):
            raise CustomException(msg=f"排课日期必须在学期范围内（{semester.start_date} 至 {semester.end_date}）")

        # 2. 验证班级
        if not data.class_ids or len(data.class_ids) == 0:
            raise CustomException(msg="请至少选择一个班级")
        
        # 验证所有班级是否存在且属于该学期
        valid_class_ids = []
        for class_id in data.class_ids:
            class_obj = await ClassCRUD(auth).get_by_id_crud(id=class_id)
            if not class_obj:
                raise CustomException(msg=f"班级ID {class_id} 不存在")
            if class_obj.semester_id != data.semester_id:
                raise CustomException(msg=f"班级ID {class_id} 不属于所选学期")
            valid_class_ids.append(class_id)

        # 3. 验证教练
        from app.api.v1.module_system.user.crud import UserCRUD
        coach = await UserCRUD(auth).get_by_id_crud(id=data.coach_id)
        if not coach:
            raise CustomException(msg="教练不存在")

        # 4. 验证时间段配置
        if not data.time_slots or len(data.time_slots) == 0:
            raise CustomException(msg="请至少选择一个时间段")
        
        # 5. 计算星期几
        day_of_week = data.schedule_date.weekday()  # 0=周一, 6=周日
        day_names = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
        day_name = day_names[day_of_week]
        
        # 从Redis获取羽毛球时间段字典（统一数据源）
        time_slot_data = await DictDataService.get_init_dict_service(
            redis=redis,
            dict_type='badminton_time_slot'
        )
        
        # 构建时间段查找字典：key=slot_code, value=time_slot_info
        time_slot_lookup = {}
        for slot in time_slot_data:
            # dict_value 是时间段代码，如 "A", "B", "C", "D", "E"
            slot_code = slot.get('dict_value', '')
            # dict_label 是时间范围，如 "08:00-09:30"
            dict_label = slot.get('dict_label', '')
            
            if '-' in dict_label:
                time_parts = dict_label.split('-')
                start_time = time_parts[0].strip()
                end_time = time_parts[1].strip()
            else:
                start_time = '08:00'
                end_time = '09:30'
            
            time_slot_lookup[slot_code] = {
                'start': start_time,
                'end': end_time,
                'duration': 90,
                'slot_code': slot_code
            }
        
        # 6. 为每个班级的每个时间段创建排课记录
        created_schedules = []
        total_attendance_count = 0
        
        for class_id in valid_class_ids:
            for target_day, slot_codes in data.time_slots.items():
                for slot_code in slot_codes:
                    # 查找时间段信息
                    if slot_code not in time_slot_lookup:
                        logger.warning(f"时间段代码 {slot_code} 不在字典中，跳过")
                        continue
                    
                    slot_info = time_slot_lookup[slot_code]
                    
                    start_time_obj = datetime.strptime(slot_info['start'], '%H:%M').time()
                    end_time_obj = datetime.strptime(slot_info['end'], '%H:%M').time()
                    duration = int(slot_info.get('duration', '90'))
                    
                    # 构建 time_slots_json (JSON 格式：{"周一": ["A", "B"]})
                    time_slots_json = json.dumps({target_day: [slot_code]}, ensure_ascii=False)
                    
                    # 准备排课数据
                    schedule_data = {
                        "class_id": class_id,
                        "schedule_date": data.schedule_date,
                        "day_of_week": day_of_week,
                        "time_slot_code": slot_code,
                        "time_slots_json": time_slots_json,
                        "start_time": start_time_obj,
                        "end_time": end_time_obj,
                        "duration_minutes": duration,
                        "schedule_type": data.schedule_type.value if hasattr(data.schedule_type, 'value') else data.schedule_type,
                        "schedule_status": data.schedule_status.value if hasattr(data.schedule_status, 'value') else data.schedule_status,
                        "coach_id": data.coach_id,
                        "location": data.location,
                        "topic": data.topic,
                        "content_summary": data.content_summary,
                        "training_focus": data.training_focus,
                        "equipment_needed": data.equipment_needed,
                        "notes": data.notes
                    }

                    # 创建排课记录
                    schedule = await ClassScheduleCRUD(auth).create_crud(data=schedule_data)
                    if not schedule:
                        raise CustomException(msg=f"创建排课记录失败（班级ID={class_id}, 时间段={target_day}{slot_code}）")

                    logger.info(f"创建排课记录成功（V2版本）：排课ID={schedule.id}, 班级ID={class_id}, 日期={data.schedule_date}, 时间段={target_day}{slot_code}, time_slots_json={time_slots_json}")

                    # 自动为选中的学员创建考勤记录
                    if data.student_ids:
                        try:
                            created_attendance_count = await cls.auto_create_attendance_service(
                                auth=auth,
                                redis=redis,
                                schedule_id=schedule.id,
                                student_ids=data.student_ids
                            )
                            total_attendance_count += created_attendance_count
                            logger.info(f"排课ID={schedule.id}：自动创建考勤记录 {created_attendance_count}/{len(data.student_ids)}")
                        except Exception as e:
                            logger.error(f"排课ID={schedule.id}：自动创建考勤记录失败：{str(e)}")
                            # 考勤创建失败不影响排课记录创建

                    created_schedules.append({
                        "id": schedule.id,
                        "schedule_date": schedule.schedule_date.isoformat(),
                        "class_id": schedule.class_id,
                        "coach_id": schedule.coach_id,
                        "time_slot_code": schedule.time_slot_code,
                        "time_slots_json": schedule.time_slots_json,
                        "schedule_status": schedule.schedule_status.value,
                        "created_at": schedule.created_time.isoformat() if schedule.created_time else None
                    })

        # 7. 返回结果
        result = {
            "count": len(created_schedules),
            "schedules": created_schedules,
            "total_attendance_count": total_attendance_count
        }

        return SimpleResponse(
            success=True,
            message=f"成功创建 {len(created_schedules)} 条排课记录",
            data=result
        ).model_dump()

    @staticmethod
    async def get_coach_daily_schedule_service(
        auth: AuthSchema,
        redis: Redis,
        coach_id: int,
        schedule_date: str
    ) -> dict:
        """
        获取教练在指定日期的排课列表（按时间段分组）

        Args:
            auth: 认证信息
            redis: Redis客户端
            coach_id: 教练ID
            schedule_date: 排课日期

        Returns:
            按时间段分组的排课数据
        """
        # 将字符串日期转换为 date 对象
        try:
            from datetime import datetime
            schedule_date_obj = datetime.strptime(schedule_date, "%Y-%m-%d").date()
        except Exception as e:
            logger.error(f"日期格式转换失败: {schedule_date}, 错误: {e}")
            return {
                "date": schedule_date,
                "coach_id": coach_id,
                "coach_name": "",
                "time_slots": []
            }
        
        # 1. 使用视图查询教练在该日期的所有排课记录（包含学员列表）
        search = {
            "coach_id": ("eq", coach_id),
            "schedule_date": ("eq", schedule_date_obj)
        }
        order_by = [{"start_time": "asc"}]
        
        # 使用新的CRUD查询视图
        schedules = await CoachScheduleCRUD(auth).list_crud(search=search, order_by=order_by)
        
        if not schedules:
            return {
                "date": schedule_date,
                "coach_id": coach_id,
                "coach_name": "",
                "time_slots": []
            }
        
        # 2. 获取教练名称（从第一条记录中获取）
        coach_name = schedules[0].get("coach_name", "")
        
        # 3. 获取时间段字典数据
        time_slot_dict_list = await get_time_slot_dict_with_cache(redis)
        
        # 将时间段列表转换为字典（以 dict_value 为键）
        time_slot_dict = {}
        for slot in time_slot_dict_list:
            if isinstance(slot, dict) and 'dict_value' in slot:
                # 解析 dict_label 获取开始和结束时间
                dict_label = slot.get('dict_label', '')
                if '-' in dict_label:
                    time_parts = dict_label.split('-')
                    start_time = time_parts[0].strip()
                    end_time = time_parts[1].strip()
                else:
                    start_time = '08:00'
                    end_time = '09:30'
                
                time_slot_dict[slot['dict_value']] = {
                    "start": start_time,
                    "end": end_time,
                    "dict_label": dict_label
                }
        
        # 4. 按时间段分组
        time_slot_groups = {}
        
        for schedule in schedules:
            # 解析 time_slots_json 获取时间段代码
            time_slot_code = schedule.get("time_slot_code")
            if not time_slot_code:
                continue
            
            # 如果该时间段还没有分组，创建分组
            if time_slot_code not in time_slot_groups:
                # 从字典中查找时间段信息
                slot_info = time_slot_dict.get(time_slot_code, {})
                time_slot_groups[time_slot_code] = {
                    "time_slot_code": time_slot_code,
                    "time_slot_name": f"{time_slot_code}时段",
                    "start_time": slot_info.get("start", ""),
                    "end_time": slot_info.get("end", ""),
                    "schedules": []
                }
            
            # 5. 从视图中获取学员列表（已经是 JSON 格式）
            students = schedule.get("students_json", [])
            if isinstance(students, str):
                try:
                    students = json.loads(students)
                except:
                    students = []
            
            # 6. 添加排课信息到分组
            time_slot_groups[time_slot_code]["schedules"].append({
                "id": schedule.get("id"),
                "class_id": schedule.get("class_id"),
                "class_name": schedule.get("class_name", ""),
                "location": schedule.get("location"),
                "topic": schedule.get("topic"),
                "content_summary": schedule.get("content_summary"),
                "schedule_status": schedule.get("schedule_status"),
                "students": students,
                "student_count": schedule.get("student_count", len(students)),
                "attendance_count": schedule.get("attendance_count", len([s for s in students if s.get("has_attended", False)])),
                "notes": schedule.get("notes")
            })
        
        # 7. 按时间段代码排序 (A, B, C, D, E, ...)
        time_slot_order = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
        sorted_time_slots = []
        
        for slot_code in time_slot_order:
            if slot_code in time_slot_groups:
                sorted_time_slots.append(time_slot_groups[slot_code])
        
        # 添加未在预定义顺序中的时间段
        for slot_code, group in time_slot_groups.items():
            if slot_code not in time_slot_order:
                sorted_time_slots.append(group)
        
        return {
            "date": schedule_date,
            "coach_id": coach_id,
            "coach_name": coach_name,
            "time_slots": sorted_time_slots
        }
