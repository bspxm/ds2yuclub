import sys
sys.path.insert(0, '/home/filter/myproject/ds2yuclub/backend')

from app.plugin.module_badminton.purchase.schema import PurchaseOutSchema
from datetime import date

# 创建一个测试对象
test_data = {
    'id': 1,
    'uuid': 'test-uuid',
    'student_id': 1,
    'class_id': 1,
    'semester_id': 1,
    'purchase_date': date(2026, 1, 31),
    'total_sessions': 32,
    'used_sessions': 0,
    'remaining_sessions': 32,
    'valid_from': date(2026, 1, 30),
    'valid_until': date(2026, 2, 6),
    'status': 'active',
    'is_settled': False,
    'original_price': 20.0,
    'actual_price': 20.0,
    'discount_rate': 1.0,
    'is_available': '0',
    'created_time': None,
    'updated_time': None,
    'created_id': None,
    'updated_id': None,
    'student': {'id': 1, 'name': '测试学员'},
    'semester': {'id': 1, 'name': '测试学期'},
    'class_ref': {'id': 1, 'name': '测试班级'},
}

# 创建 Schema 实例
schema = PurchaseOutSchema(**test_data)

# 序列化为字典
result = schema.model_dump()

print("序列化结果:")
print(f"session_count: {result.get('session_count')}")
print(f"total_amount: {result.get('total_amount')}")
print(f"unit_price: {result.get('unit_price')}")
print(f"purchase_type: {result.get('purchase_type')}")
print(f"start_date: {result.get('start_date')}")
print(f"end_date: {result.get('end_date')}")

print("\n完整结果:")
import json
print(json.dumps(result, indent=2, default=str))