"""
purchase模块 - Service服务层
"""

from datetime import date, datetime, timedelta
from typing import Optional, List, Dict, Any
from redis.asyncio.client import Redis

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
from ..cache_utils import BadmintonCache, BadmintonCacheKeys, CacheExpireTime

# ============================================================================
# 购买记录管理服务
# ============================================================================

class PurchaseService:
    """购买记录管理服务层"""

    @classmethod
    async def get_remaining_sessions_cached(cls, auth: AuthSchema, redis: Redis, student_id: int, class_id: int) -> int:
        """
        获取学员剩余课时（带Redis缓存）

        Args:
            auth: 认证信息
            redis: Redis客户端
            student_id: 学员ID
            class_id: 班级ID

        Returns:
            int: 剩余课时数
        """
        cache_key = f"{BadmintonCacheKeys.STUDENT_SESSIONS}:{student_id}:{class_id}"

        # 尝试从Redis缓存获取
        cached_sessions = await BadmintonCache.get_json(redis, cache_key)
        if cached_sessions is not None:
            return int(cached_sessions)

        # 从数据库查询
        purchases = await PurchaseCRUD(auth).list(
            search={
                "student_id": ("eq", student_id),
                "class_id": ("eq", class_id)
            }
        )

        # 获取最新购买记录的剩余课时
        remaining_sessions = 0
        if purchases:
            remaining_sessions = purchases[0].remaining_sessions

        # 存入Redis缓存
        await BadmintonCache.set_json(redis, cache_key, remaining_sessions, CacheExpireTime.STUDENT_SESSIONS)

        return remaining_sessions

    @classmethod
    async def detail_service(cls, auth: AuthSchema, purchase_id: int) -> dict:
        """获取购买记录详情"""
        purchase = await PurchaseCRUD(auth).get_by_id_crud(
            id=purchase_id,
            preload=["student", "class_ref", "semester", "created_by", "updated_by"]
        )
        if not purchase:
            raise CustomException(msg="购买记录不存在")
        return PurchaseOutSchema.model_validate(purchase).model_dump()

    @classmethod
    async def list_service(cls, auth: AuthSchema, search: Optional[dict] = None, order_by: Optional[list[dict]] = None) -> list[dict]:
        """购买记录列表查询"""
        purchases = await PurchaseCRUD(auth).list_crud(
            search=search,
            order_by=order_by,
            preload=["student", "class_ref", "semester"]
        )
        return [PurchaseOutSchema.model_validate(purchase).model_dump() for purchase in purchases]

    @classmethod
    async def page_service(cls, auth: AuthSchema, page_no: int, page_size: int, search: Optional[dict | PurchaseQueryParam] = None, order_by: Optional[list[dict]] = None) -> dict:
        """购买记录分页查询"""
        # 将QueryParam对象转换为字典
        if isinstance(search, PurchaseQueryParam):
            search_dict = vars(search)
        else:
            search_dict = search or {}

        order_by_list = order_by or [{'id': 'asc'}]
        offset = (page_no - 1) * page_size

        # 不使用 out_schema，直接获取原始对象以避免加载过多关联数据
        result = await PurchaseCRUD(auth).page_crud(
            offset=offset,
            limit=page_size,
            order_by=order_by_list,
            search=search_dict,
            preload=["student", "class_ref", "semester"],
            out_schema=None
        )

        import json
        # 手动构建返回数据，只包含必要的字段
        items = []
        for purchase in result["items"]:
            # 转换 selected_time_slots 从 JSON 字符串到字典
            selected_time_slots_dict = None
            if purchase.selected_time_slots:
                try:
                    selected_time_slots_dict = json.loads(purchase.selected_time_slots)
                except (json.JSONDecodeError, ValueError):
                    selected_time_slots_dict = None
            
            item = {
                'id': purchase.id,
                'uuid': purchase.uuid,
                'student_id': purchase.student_id,
                'class_id': purchase.class_id,
                'semester_id': purchase.semester_id,
                'purchase_date': purchase.purchase_date.isoformat() if purchase.purchase_date else None,
                'total_sessions': purchase.total_sessions,
                'used_sessions': purchase.used_sessions,
                'remaining_sessions': purchase.remaining_sessions,
                'carry_over_sessions': purchase.carry_over_sessions,
                'credit_sessions': purchase.credit_sessions,
                'valid_from': purchase.valid_from.isoformat() if purchase.valid_from else None,
                'valid_until': purchase.valid_until.isoformat() if purchase.valid_until else None,
                'status': purchase.status.value if purchase.status else None,
                'is_settled': purchase.is_settled,
                'settlement_date': purchase.settlement_date.isoformat() if purchase.settlement_date else None,
                'original_price': purchase.original_price,
                'actual_price': purchase.actual_price,
                'discount_rate': purchase.discount_rate,
                'purchase_notes': purchase.purchase_notes,
                'selected_time_slots': selected_time_slots_dict,
                'description': purchase.description,
                'created_time': purchase.created_time.isoformat() if purchase.created_time else None,
                'updated_time': purchase.updated_time.isoformat() if purchase.updated_time else None,
                # 关联对象
                'student': {
                    'id': purchase.student.id,
                    'name': purchase.student.name
                } if purchase.student else None,
                'class_ref': {
                    'id': purchase.class_ref.id,
                    'name': purchase.class_ref.name
                } if purchase.class_ref else None,
                'semester': {
                    'id': purchase.semester.id,
                    'name': purchase.semester.name
                } if purchase.semester else None,
            }
            items.append(item)

        return {
            "total": result["total"],
            "page_no": page_no,
            "page_size": page_size,
            "items": items
        }

    @classmethod
    async def create_service(cls, auth: AuthSchema, redis: Redis, data: PurchaseCreateSchema) -> dict:
        """创建购买记录（带缓存失效）"""
        # 检查学员是否已购买该班级（同一学期内）
        # TODO: 实现重复购买检查

        # 保存原始购买课时数
        original_total = data.total_sessions

        # 转换 selected_time_slots 为 JSON 字符串存储
        import json
        purchase_data = data.model_dump(exclude_none=True)
        if purchase_data.get('selected_time_slots') is not None:
            purchase_data['selected_time_slots'] = json.dumps(purchase_data['selected_time_slots'])
        
        # 检查是否有结转课时可以应用
        carry_over_sessions = 0
        carry_over_details = []
        
        # 查找该学员之前学期的结转课时（已结算且剩余课时>0的购买记录）
        previous_purchases = await PurchaseCRUD(auth).list_crud(
            search={
                "student_id": data.student_id,
                "is_settled": True,
                "remaining_sessions": ("gt", 0)  # 剩余课时大于0
            },
            order_by=[{"settlement_date": "desc"}]
        )
        
        # 计算总结转课时
        for prev_purchase in previous_purchases:
            if prev_purchase.remaining_sessions > 0:
                carry_over_sessions += prev_purchase.remaining_sessions
                carry_over_details.append({
                    "previous_purchase_id": prev_purchase.id,
                    "previous_semester": prev_purchase.semester.name if prev_purchase.semester else "未知学期",
                    "carry_over_sessions": prev_purchase.remaining_sessions,
                    "original_total": prev_purchase.total_sessions,
                    "original_used": prev_purchase.used_sessions
                })
        
        # 如果有结转课时，更新购买数据
        if carry_over_sessions > 0:
            # 总课时 = 新购买课时 + 结转课时
            new_total_sessions = original_total + carry_over_sessions
            purchase_data["total_sessions"] = new_total_sessions
            purchase_data["carry_over_sessions"] = carry_over_sessions
            purchase_data["purchase_notes"] = (
                f"{purchase_data.get('purchase_notes', '')} "
                f"[包含结转课时：{carry_over_sessions}节，来自{len(carry_over_details)}个历史购买]"
            ).strip()

        # 计算并设置剩余课时
        purchase_data["remaining_sessions"] = purchase_data.get("total_sessions", 0) - purchase_data.get("used_sessions", 0)

        # 创建购买记录
        purchase = await PurchaseCRUD(auth).create_crud(data=purchase_data)
        if not purchase:
            raise CustomException(msg="创建购买记录失败")
        
        # 如果有结转课时，更新历史购买记录的结转状态
        if carry_over_sessions > 0:
            for detail in carry_over_details:
                # 将历史购买记录的剩余课时清零（因为已结转）
                await PurchaseCRUD(auth).update_crud(
                    id=detail["previous_purchase_id"],
                    data={"remaining_sessions": 0, "carry_over_sessions": 0}
                )
        
        response_data = PurchaseOutSchema.model_validate(purchase).model_dump()

        # 添加结转信息到响应
        if carry_over_sessions > 0:
            response_data["carry_over_info"] = {
                "applied_carry_over_sessions": carry_over_sessions,
                "original_purchased_sessions": original_total,
                "new_total_sessions": purchase.total_sessions,
                "carry_over_details": carry_over_details
            }

        # 失效学员课时缓存
        cache_key = f"{BadmintonCacheKeys.STUDENT_SESSIONS}:{data.student_id}:{data.class_id}"
        await BadmintonCache.delete_pattern(redis, cache_key)

        return SimpleResponse(
            success=True,
            message=f"购买记录创建成功{'（已应用结转课时）' if carry_over_sessions > 0 else ''}",
            data=response_data
        ).model_dump()

    @classmethod
    async def batch_create_service(cls, auth: AuthSchema, redis: Redis, data: BatchPurchaseCreateSchema) -> dict:
        """批量创建购买记录"""
        results = []
        success_count = 0
        failed_count = 0

        # 遍历每个学员ID，创建购买记录
        for student_id in data.student_ids:
            try:
                # 为每个学员创建购买记录
                import json
                purchase_data = {
                    "student_id": student_id,
                    "class_id": data.class_id,
                    "semester_id": data.semester_id,
                    "purchase_date": data.purchase_date,
                    "total_sessions": data.total_sessions,
                    "valid_from": data.valid_from,
                    "valid_until": data.valid_until,
                    "original_price": data.original_price,
                    "actual_price": data.actual_price,
                    "discount_rate": data.discount_rate,
                    "purchase_notes": data.purchase_notes
                }

                # 添加时间段（保持原始格式，让 Schema 验证器处理）
                if hasattr(data, 'selected_time_slots') and data.selected_time_slots:
                    purchase_data['selected_time_slots'] = data.selected_time_slots
                
                # 将字典转换为 PurchaseCreateSchema 对象
                purchase_schema = PurchaseCreateSchema(**purchase_data)
                
                # 调用单个创建服务
                result = await cls.create_service(auth, redis, purchase_schema)
                
                # 只取 data 部分，不嵌套整个 SimpleResponse
                purchase_data_result = result.get("data", result)
                
                results.append({
                    "student_id": student_id,
                    "success": True,
                    "data": purchase_data_result
                })
                success_count += 1
                
            except Exception as e:
                logger.error(f"批量创建购买记录失败 - 学员ID: {student_id}, 错误: {str(e)}")
                results.append({
                    "student_id": student_id,
                    "success": False,
                    "error": str(e)
                })
                failed_count += 1
        
        return SimpleResponse(
            success=failed_count == 0,
            message=f"批量创建完成：成功{success_count}条，失败{failed_count}条",
            data={
                "total": len(data.student_ids),
                "success_count": success_count,
                "failed_count": failed_count,
                "results": results
            }
        ).model_dump()

    @classmethod
    async def update_service(cls, auth: AuthSchema, redis: Redis, purchase_id: int, data: PurchaseUpdateSchema) -> dict:
        """更新购买记录（带缓存失效）"""
        # 转换 selected_time_slots 为 JSON 字符串存储
        import json
        update_data = data.model_dump(exclude_none=True)
        if update_data.get('selected_time_slots') is not None:
            update_data['selected_time_slots'] = json.dumps(update_data['selected_time_slots'])

        # 获取原始购买记录
        original_purchase = await PurchaseCRUD(auth).get_by_id_crud(id=purchase_id)
        if not original_purchase:
            raise CustomException(msg="购买记录不存在")

        # 计算剩余课时
        total_sessions = update_data.get("total_sessions", original_purchase.total_sessions)
        used_sessions = update_data.get("used_sessions", original_purchase.used_sessions)
        update_data["remaining_sessions"] = total_sessions - used_sessions

        purchase = await PurchaseCRUD(auth).update_crud(id=purchase_id, data=update_data)
        if not purchase:
            raise CustomException(msg="购买记录不存在或更新失败")

        # 失效学员课时缓存
        cache_key = f"{BadmintonCacheKeys.STUDENT_SESSIONS}:{original_purchase.student_id}:{original_purchase.class_id}"
        await BadmintonCache.delete_pattern(redis, cache_key)

        return SimpleResponse(
            success=True,
            message="购买记录更新成功",
            data=PurchaseOutSchema.model_validate(purchase).model_dump()
        ).model_dump()

    @classmethod
    async def delete_service(cls, auth: AuthSchema, purchase_ids: list[int]) -> dict:
        """删除购买记录"""
        await PurchaseCRUD(auth).delete_crud(ids=purchase_ids)
        return SimpleResponse(
            success=True,
            message="购买记录删除成功"
        ).model_dump()

    @classmethod
    async def settle_purchase_service(cls, auth: AuthSchema, purchase_id: int) -> dict:
        """结算单个购买记录"""
        from datetime import date
        from ..enums import PurchaseStatusEnum
        
        # 获取购买记录
        purchase = await PurchaseCRUD(auth).get_by_id_crud(id=purchase_id)
        if not purchase:
            raise CustomException(msg="购买记录不存在")
        
        # 检查是否已结算
        if purchase.is_settled:
            raise CustomException(msg="该购买记录已结算")
        
        # 计算剩余课时：总课时 - 已使用课时
        remaining_sessions = purchase.total_sessions - purchase.used_sessions
        
        # 计算信用欠课时（如果已使用课时超过总课时）
        credit_sessions = 0
        if purchase.used_sessions > purchase.total_sessions:
            credit_sessions = purchase.used_sessions - purchase.total_sessions
            remaining_sessions = 0  # 欠课时时，剩余课时为0
        
        # 更新购买记录
        update_data = {
            "remaining_sessions": remaining_sessions,
            "credit_sessions": credit_sessions,
            "is_settled": True,
            "settlement_date": date.today(),
            "status": PurchaseStatusEnum.SETTLED
        }
        
        settled_purchase = await PurchaseCRUD(auth).update_crud(
            id=purchase_id,
            data=PurchaseUpdateSchema(**update_data)
        )
        
        if not settled_purchase:
            raise CustomException(msg="购买记录结算失败")
        
        return SimpleResponse(
            success=True,
            message="购买记录结算成功",
            data={
                "purchase": PurchaseOutSchema.model_validate(settled_purchase).model_dump(),
                "settlement_summary": {
                    "total_sessions": purchase.total_sessions,
                    "used_sessions": purchase.used_sessions,
                    "remaining_sessions": remaining_sessions,
                    "credit_sessions": credit_sessions,
                    "can_carry_over": remaining_sessions > 0
                }
            }
        ).model_dump()

    @classmethod
    async def settle_semester_purchases_service(cls, auth: AuthSchema, semester_id: int) -> dict:
        """结算指定学期的所有购买记录"""
        from datetime import date
        from ..enums import PurchaseStatusEnum
        
        # 获取该学期所有未结算的购买记录
        purchases = await PurchaseCRUD(auth).list_crud(
            search={
                "semester_id": semester_id,
                "is_settled": False,
                "status": PurchaseStatusEnum.ACTIVE
            }
        )
        
        if not purchases:
            raise CustomException(msg="该学期没有需要结算的购买记录")
        
        settlement_results = []
        total_remaining = 0
        total_credit = 0
        
        # 结算每个购买记录
        for purchase in purchases:
            # 计算剩余课时
            remaining_sessions = purchase.total_sessions - purchase.used_sessions
            credit_sessions = 0
            
            if purchase.used_sessions > purchase.total_sessions:
                credit_sessions = purchase.used_sessions - purchase.total_sessions
                remaining_sessions = 0
            
            # 更新购买记录
            update_data = {
                "remaining_sessions": remaining_sessions,
                "credit_sessions": credit_sessions,
                "carry_over_sessions": remaining_sessions,  # 剩余课时自动转为结转课时
                "is_settled": True,
                "settlement_date": date.today(),
                "status": PurchaseStatusEnum.SETTLED
            }
            
            settled_purchase = await PurchaseCRUD(auth).update_crud(
                id=purchase.id,
                data=PurchaseUpdateSchema(**update_data)
            )
            
            if settled_purchase:
                total_remaining += remaining_sessions
                total_credit += credit_sessions
                
                settlement_results.append({
                    "purchase_id": purchase.id,
                    "student_name": purchase.student.name if purchase.student else "未知学员",
                    "class_name": purchase.class_ref.name if purchase.class_ref else "未知班级",
                    "total_sessions": purchase.total_sessions,
                    "used_sessions": purchase.used_sessions,
                    "remaining_sessions": remaining_sessions,
                    "credit_sessions": credit_sessions,
                    "success": True
                })
            else:
                settlement_results.append({
                    "purchase_id": purchase.id,
                    "student_name": purchase.student.name if purchase.student else "未知学员",
                    "class_name": purchase.class_ref.name if purchase.class_ref else "未知班级",
                    "success": False,
                    "error": "更新失败"
                })
        
        # 统计成功和失败的结算
        successful_settlements = [r for r in settlement_results if r["success"]]
        failed_settlements = [r for r in settlement_results if not r["success"]]
        
        return SimpleResponse(
            success=True,
            message=f"学期结算完成：成功{len(successful_settlements)}条，失败{len(failed_settlements)}条",
            data={
                "semester_id": semester_id,
                "total_purchases": len(purchases),
                "successful_settlements": len(successful_settlements),
                "failed_settlements": len(failed_settlements),
                "total_remaining_sessions": total_remaining,
                "total_credit_sessions": total_credit,
                "settlement_results": settlement_results,
                "summary": {
                    "剩余总课时可结转": total_remaining,
                    "信用欠课时总计": total_credit,
                    "平均每学员剩余课时": total_remaining / len(successful_settlements) if successful_settlements else 0
                }
            }
        ).model_dump()
