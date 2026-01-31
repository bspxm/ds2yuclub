"""add_badminton_time_slot_dict

Revision ID: add_badminton_time_slot
Revises: 
Create Date: 2026-01-30

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_badminton_time_slot'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 添加羽毛球时间段字典类型
    op.execute("""
        INSERT INTO sys_dict_type (dict_name, dict_type, status, description, created_time, updated_time, uuid)
        VALUES ('羽毛球时间段', 'badminton_time_slot', '0', '羽毛球培训班时间段', NOW(), NOW(), gen_random_uuid())
        ON CONFLICT (dict_type) DO NOTHING;
    """)

    # 获取字典类型ID
    result = op.execute("""
        SELECT id FROM sys_dict_type WHERE dict_type = 'badminton_time_slot'
    """)
    dict_type_id = result.fetchone()[0] if result else None

    if dict_type_id:
        # 添加时间段数据
        op.execute(f"""
            INSERT INTO sys_dict_data (dict_sort, dict_label, dict_value, dict_type, dict_type_id, css_class, list_class, is_default, status, description, created_time, updated_time, uuid)
            VALUES
                (1, '08:00-09:30', 'A', 'badminton_time_slot', {dict_type_id}, '', 'primary', false, '0', 'A时间段：上午时段', NOW(), NOW(), gen_random_uuid()),
                (2, '09:30-11:00', 'B', 'badminton_time_slot', {dict_type_id}, '', 'success', false, '0', 'B时间段：上午时段', NOW(), NOW(), gen_random_uuid()),
                (3, '14:00-15:30', 'C', 'badminton_time_slot', {dict_type_id}, '', 'info', false, '0', 'C时间段：下午时段', NOW(), NOW(), gen_random_uuid()),
                (4, '15:30-17:00', 'D', 'badminton_time_slot', {dict_type_id}, '', 'warning', false, '0', 'D时间段：下午时段', NOW(), NOW(), gen_random_uuid()),
                (5, '18:00-19:30', 'E', 'badminton_time_slot', {dict_type_id}, '', 'danger', false, '0', 'E时间段：晚上时段', NOW(), NOW(), gen_random_uuid())
            ON CONFLICT DO NOTHING;
        """)


def downgrade():
    # 删除时间段数据
    op.execute("""
        DELETE FROM sys_dict_data WHERE dict_type = 'badminton_time_slot'
    """)

    # 删除字典类型
    op.execute("""
        DELETE FROM sys_dict_type WHERE dict_type = 'badminton_time_slot'
    """)