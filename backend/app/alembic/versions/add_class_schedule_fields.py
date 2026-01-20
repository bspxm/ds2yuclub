"""add_class_schedule_fields

Revision ID: add_class_schedule
Revises: add_wintersummer
Create Date: 2026-01-20 23:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_class_schedule'
down_revision: Union[str, None] = 'add_wintersummer'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 为班级表添加每周排班相关字段
    op.add_column('badminton_class', sa.Column('weekly_schedule', sa.String(length=256), nullable=True, comment='每周排班(如：周一、周三、周五)'))
    op.add_column('badminton_class', sa.Column('time_slots_json', sa.Text(), nullable=True, comment='时间段JSON配置'))
    op.add_column('badminton_class', sa.Column('location', sa.String(length=128), nullable=True, comment='上课地点'))
    op.add_column('badminton_class', sa.Column('fee_per_session', sa.Float(), nullable=True, comment='每节课费用'))


def downgrade() -> None:
    # 删除添加的字段
    op.drop_column('badminton_class', 'fee_per_session')
    op.drop_column('badminton_class', 'location')
    op.drop_column('badminton_class', 'time_slots_json')
    op.drop_column('badminton_class', 'weekly_schedule')