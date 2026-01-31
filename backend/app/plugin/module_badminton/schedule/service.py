"""
schedule模块 - Service服务层
"""

from datetime import date, datetime, timedelta
from typing import Optional, List, Dict, Any
from redis.asyncio.client import Redis
from sqlalchemy.orm import Session

from app.api.v1.module_system.user.service import UserService
from app.core.base_crud import CRUDBase
from app.core.database import SessionDep
from app.core.exceptions import CustomException
from app.core.logger import logger

from .model import *
from .crud import *
from ..class_.schema import (
    ClassScheduleCreateV2Schema,
    ClassScheduleOutSchema,
    ClassScheduleQueryParam,
    AvailableStudentSchema,
    ClassAttendanceCreateSchema,
    ClassAttendanceUpdateSchema
)
from app.common.response import PaginatedResponse
from ..response import SimpleResponse
from app.api.v1.module_system.auth.schema import AuthSchema
from app.api.v1.module_system.dict.service import DictDataService

# ============================================================================
# 羽毛球时间段代码映射（支持扩展到J，无数量限制）
# 格式：{day_index}{slot_code}，例如：0A, 6A, 6J
# ============================================================================

TIME_SLOT_CODES = {
    1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E',
    6: 'F', 7: 'G', 8: 'H', 9: 'I', 10: 'J'
}

def get_time_slot_info_by_dict(time_slot_id: str | int, time_slot_dict: dict) -> dict:
    """
    根据时间槽ID获取时间段信息（从字典中获取）
    
    参数：
        time_slot_id: 完整的时间槽ID（字符串格式：{day_index}{slot_code}）
        time_slot_dict: 字典数据列表，格式为 [{id, dict_value, start, end, duration}, ...]
    
    返回：
        dict: 包含 start_time_str, end_time_str, duration_minutes, slot_code, day_index 的字典
    """
    # 确保time_slot_id是字符串
    if isinstance(time_slot_id, int):
        time_slot_id_str = str(time_slot_id)
    else:
        time_slot_id_str = time_slot_id
    
    if not time_slot_id_str or not time_slot_dict:
        raise ValueError("time_slot_id 和 time_slot_dict 不能为空")
    
    # 解析ID格式：{day_index}{slot_code}
    day_index = time_slot_id_str[:-1]  # 提取星期几（前部分）
    slot_code = time_slot_id_str[-1]  # 提取时段代码（最后一位）
    
    # 从字典中查找对应的时间段
    time_slot = None
    for item in time_slot_dict:
        if item.get('dict_value') == time_slot_id_str:
            time_slot = item
            break
    
    if not time_slot:
        raise ValueError(f"时间段ID {time_slot_id_str} 在字典中不存在")
    
    return {
        'start_time_str': time_slot.get('start'),
        'end_time_str': time_slot.get('end'),
        'duration_minutes': int(time_slot.get('duration', '90')),
        'slot_code': slot_code,
        'day_index': int(day_index) if day_index.isdigit() else 0,
        'id': time_slot_id_str
    }

# ============================================================================
# 排课记录管理服务
# ============================================================================

class ClassScheduleService:
    """排课记录管理服务层"""

    @classmethod
    async def detail_service(cls, auth: AuthSchema, schedule_id: int) -> dict:
        """获取排课记录详情"""
        logger.info(f"获取排课记录详情，schedule_id={schedule_id}")
        schedule = await ClassScheduleCRUD(auth).get_by_id_crud(
            id=schedule_id,
            preload=["class_ref", "coach_user", "created_by", "updated_by", "attendance_records"]
        )
        if not schedule:
            raise CustomException(msg="排课记录不存在")
        
        logger.info(f"排课记录加载成功，attendance_records={schedule.attendance_records}")
        
        # 使用 Schema 序列化数据
        data = ClassScheduleOutSchema.model_validate(schedule).model_dump()
        
        # 手动添加 semester_id（从 class_ref 中获取）
        if schedule.class_ref:
            data['semester_id'] = schedule.class_ref.semester_id
        
        # 添加学员ID列表（从考勤记录中提取）
        if schedule.attendance_records:
            student_ids = [att.student_id for att in schedule.attendance_records if att.student_id]
            data['student_ids'] = student_ids
            logger.info(f"从考勤记录中提取学员IDs: {student_ids}")
        else:
            data['student_ids'] = []
            logger.info(f"没有考勤记录，student_ids=[]")
        
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
        """排课记录分页查询"""
        # 将QueryParam对象转换为字典
        if isinstance(search, ClassScheduleQueryParam):
            search_dict = vars(search)
        else:
            search_dict = search or {}

        order_by_list = order_by or [{'id': 'asc'}]
        offset = (page_no - 1) * page_size

        # 不使用 out_schema，直接获取原始对象以避免加载过多关联数据
        result = await ClassScheduleCRUD(auth).page_crud(
            offset=offset,
            limit=page_size,
            order_by=order_by_list,
            search=search_dict,
            preload=["class_ref", "coach_user", "attendance_records"],
            out_schema=None
        )

        # 手动构建返回数据，只包含必要的字段
        items = []
        for schedule in result["items"]:
            # 计算学员数（从考勤记录中统计）
            student_count = 0
            if hasattr(schedule, 'attendance_records') and schedule.attendance_records:
                student_count = len(schedule.attendance_records)
            
            item = {
                'id': schedule.id,
                'uuid': schedule.uuid,
                'class_id': schedule.class_id,
                'schedule_date': schedule.schedule_date.isoformat() if schedule.schedule_date else None,
                'day_of_week': schedule.day_of_week,
                'time_slot_id': schedule.time_slot_id,
                'time_slot_code': schedule.time_slot_code,
                'time_slots_json': schedule.time_slots_json,
                'start_time': schedule.start_time.isoformat() if schedule.start_time else None,
                'end_time': schedule.end_time.isoformat() if schedule.end_time else None,
                'duration_minutes': schedule.duration_minutes,
                'schedule_type': schedule.schedule_type.value if schedule.schedule_type else None,
                'schedule_status': schedule.schedule_status.value if schedule.schedule_status else None,
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
                # 关联对象
                'class': {
                    'id': schedule.class_ref.id,
                    'name': schedule.class_ref.name,
                    'semester_id': schedule.class_ref.semester_id
                } if schedule.class_ref else None,
                'coach': {
                    'id': schedule.coach_user.id,
                    'name': schedule.coach_user.name
                } if schedule.coach_user else None,
            }
            items.append(item)

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
        
        # 如果提供了 time_slot_id，填充时间字段
        if "time_slot_id" in data_dict and data_dict["time_slot_id"]:
            # 从Redis获取羽毛球时间段字典
            time_slot_data = await DictDataService.get_init_dict_service(
                redis=redis,
                dict_type='badminton_time_slot'
            )
            
            # 使用统一的时间段解析函数
            time_slot_info = get_time_slot_info_by_dict(data_dict["time_slot_id"], time_slot_data)
            
            # 填充时间字段
            if "start_time" not in data_dict or data_dict["start_time"] is None:
                data_dict["start_time"] = datetime.strptime(time_slot_info['start_time_str'], '%H:%M').time()
            if "end_time" not in data_dict or data_dict["end_time"] is None:
                data_dict["end_time"] = datetime.strptime(time_slot_info['end_time_str'], '%H:%M').time()
            if "duration_minutes" not in data_dict or data_dict["duration_minutes"] is None:
                data_dict["duration_minutes"] = time_slot_info['duration_minutes']
        
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
                # 1. 删除旧的考勤记录
                from app.plugin.module_badminton.attendance import ClassAttendanceCRUD
                old_attendance = await ClassAttendanceCRUD(auth).list(search={"schedule_id": schedule_id})
                if old_attendance:
                    old_attendance_ids = [att.id for att in old_attendance]
                    await ClassAttendanceCRUD(auth).delete_crud(ids=old_attendance_ids)
                    logger.info(f"排课ID={schedule_id}：删除旧考勤记录 {len(old_attendance_ids)} 条")
                
                # 2. 为新的学员列表创建考勤记录
                if student_ids and len(student_ids) > 0:
                    created_count = await cls.auto_create_attendance_service(
                        auth=auth,
                        redis=redis,
                        schedule_id=schedule_id,
                        student_ids=student_ids
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

            # 准备时间段ID列表
            time_slot_ids = []
            if original_schedule.time_slot_id:
                time_slot_ids = [original_schedule.time_slot_id]

            # 创建新的排课记录（补课）
            new_schedule_data = ClassScheduleCreateV2Schema(
                semester_id=original_schedule.class_ref.semester_id if original_schedule.class_ref else 1,
                schedule_date=next_week_date,
                class_ids=[original_schedule.class_id],
                coach_id=original_schedule.coach_id,
                time_slot_ids=time_slot_ids,
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
    async def get_available_students_service(cls, auth: AuthSchema, semester_id: int,
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
        from app.plugin.module_badminton.class_.crud import ClassCRUD
        from app.plugin.module_badminton.purchase.crud import PurchaseCRUD

        # 1. 查询班级（如果未提供class_ids则查询该学期下所有班级）
        if class_ids and len(class_ids) > 0:
            # 查询指定班级
            classes = await ClassCRUD(auth).list_crud(
                search={"id": ("in", class_ids)}
            )
        else:
            # 查询该学期下所有班级
            classes = await ClassCRUD(auth).list_crud(
                search={"semester_id": ("eq", semester_id)}
            )
        
        if not classes:
            return []

        target_class_ids = [c.id for c in classes]

        # 2. 查询这些班级的购买记录
        purchases = await PurchaseCRUD(auth).list(
            search={"class_id": ("in", target_class_ids)},
            preload=["student"]
        )
        if not purchases:
            return []

        available_students = []
        day_names = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
        day_of_week = schedule_date.weekday()  # 0=周一, 6=周日
        # 转换为中文星期名称
        day_name = day_names[day_of_week]

        # time_slots 已经是 JSON 格式: {'周一': ['A', 'B'], '周二': ['C']}
        target_slots = time_slots

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

            # 添加调试日志
            if purchase.student:
                logger.info(f"检查学员: {purchase.student.name}, 购买记录selected_time_slots: {selected_slots}, 目标时间段: {target_slots}, 匹配: {has_matching_slot}, 剩余课时: {purchase.remaining_sessions}, 有效期: {purchase.valid_from} ~ {purchase.valid_until}")

            if not has_matching_slot:
                continue

            # 4. 检查学员是否有剩余课时
            if purchase.remaining_sessions <= 0:
                logger.info(f"学员 {purchase.student.name} 剩余课时不足: {purchase.remaining_sessions}")
                continue

            # 5. 检查排课日期是否在购买记录的有效期内
            if not (purchase.valid_from <= schedule_date <= purchase.valid_until):
                logger.info(f"学员 {purchase.student.name} 排课日期不在有效期内: {schedule_date} 不在 {purchase.valid_from} ~ {purchase.valid_until} 之间")
                continue

            # 添加到可用学员列表
            student = purchase.student
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

        logger.info(f"获取可用学员列表：学期ID={semester_id}, 日期={schedule_date}, 时间段={time_slots}, 班级ID={class_ids if class_ids else '全部'}, 学员数={len(available_students)}")

        return available_students

    @classmethod
    async def auto_create_attendance_service(cls, auth: AuthSchema, schedule_id: int, 
                                           student_ids: list[int]) -> int:
        """
        为排课记录自动创建考勤记录

        逻辑：
        1. 获取排课记录信息
        2. 获取班级的时间段配置
        3. 根据 time_slot_id 获取时间段信息
        4. 为每个学员查找对应的购买记录
        5. 创建考勤记录（默认状态：PRESENT）
        6. 自动扣减课时

         Args:
             auth: 认证信息
             redis: Redis客户端
             schedule_id: 排课记录ID
             student_ids: 学员ID列表

        Returns:
            int: 创建的考勤记录数量
        """
        import json
        from datetime import time
        from app.plugin.module_badminton.attendance import ClassAttendanceCRUD
        from app.plugin.module_badminton.attendance.model import AttendanceStatusEnum
        from app.plugin.module_badminton.purchase.crud import PurchaseCRUD
        from app.plugin.module_badminton.schedule.model import ClassScheduleModel

        # 1. 获取排课记录
        schedule = await ClassScheduleCRUD(auth).get_by_id_crud(
            id=schedule_id,
            preload=["class_ref"]
        )
        if not schedule:
            raise CustomException(msg="排课记录不存在")

        # 2. 获取班级的时间段配置
        class_obj = schedule.class_ref
        if not class_obj or not class_obj.time_slots_json:
            raise CustomException(msg="班级时间段配置不存在")
        
        # 3. 根据 time_slot_id 从字典获取时间段信息（V2版本）
        if schedule.time_slot_id is None:
            raise CustomException(msg=f"排课记录缺少时间段ID（V2版本必须设置time_slot_id）")
        
        # 从Redis获取羽毛球时间段字典
        time_slot_data = await DictDataService.get_init_dict_service(
            redis=redis,
            dict_type='badminton_time_slot'
        )
        
        # 使用统一的时间段解析函数
        time_slot_info = get_time_slot_info_by_dict(schedule.time_slot_id, time_slot_data)
        
        start_time_str = time_slot_info['start_time_str']
        end_time_str = time_slot_info['end_time_str']
        duration_minutes = time_slot_info['duration_minutes']
        
        # 转换为time对象
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        end_time = datetime.strptime(end_time_str, '%H:%M').time()
        
        created_count = 0

        # 4. 为每个学员创建考勤记录
        for student_id in student_ids:
            # 查找学员的购买记录
            purchases = await PurchaseCRUD(auth).list(
                search={
                    "student_id": ("eq", student_id),
                    "class_id": ("eq", schedule.class_id)
                }
            )
            
            if not purchases:
                logger.warning(f"学员{student_id}没有购买班级{schedule.class_id}的课时包")
                continue

            # 使用最近购买的课时包
            purchase = purchases[0]

            # 检查是否有剩余课时
            if purchase.remaining_sessions <= 0:
                logger.warning(f"学员{student_id}的课时包{purchase.id}没有剩余课时")
                continue

            # 5. 创建考勤记录
            attendance = await ClassAttendanceCRUD(auth).create_crud(
                data={
                    "student_id": student_id,
                    "class_id": schedule.class_id,
                    "schedule_id": schedule_id,
                    "purchase_id": purchase.id,
                    "attendance_date": schedule.schedule_date,  # 直接传递 date 对象
                    "start_time": start_time,  # 直接传递 time 对象
                    "end_time": end_time,  # 直接传递 time 对象
                    "duration_minutes": duration_minutes,
                    "attendance_status": AttendanceStatusEnum.PRESENT,
                    "session_deducted": 1,
                    "is_auto_deduct": True,
                    "coach_id": schedule.coach_id
                }
            )
            if attendance:
                created_count += 1

            attendance = await ClassAttendanceCRUD(auth).create_crud(data=attendance_data)
            if attendance:
                created_count += 1
                
                # 6. 自动扣减课时
                await PurchaseCRUD(auth).update_crud(
                    id=purchase.id,
                    data={
                        "used_sessions": purchase.used_sessions + 1,
                        "remaining_sessions": purchase.remaining_sessions - 1
                    }
                )
                
                logger.info(f"为学员{student_id}创建考勤记录成功，已扣减1课时")

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
        from app.plugin.module_badminton.class_.crud import ClassCRUD
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
                    
                    # 生成 time_slot_id (保留用于兼容)：day_index*10+slot_code_idx
                    day_idx_lookup = day_names.index(target_day)
                    slot_code_idx_lookup = ord(slot_code) - ord('A') + 1
                    time_slot_id = day_idx_lookup * 10 + slot_code_idx_lookup
                    
                    # 准备排课数据
                    schedule_data = {
                        "class_id": class_id,
                        "schedule_date": data.schedule_date,
                        "day_of_week": day_of_week,
                        "time_slot_id": time_slot_id,
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
                        "time_slot_id": schedule.time_slot_id,
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
