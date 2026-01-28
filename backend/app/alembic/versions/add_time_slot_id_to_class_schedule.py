"""add_time_slot_id_to_class_schedule

Revision ID: add_time_slot_id
Revises: f7f80e0ada53
Create Date: 2026-01-28 00:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_time_slot_id'
down_revision: Union[str, None] = 'f7f80e0ada53'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 添加 time_slot_id 列到 badminton_class_schedule 表
    op.add_column('badminton_class_schedule', sa.Column('time_slot_id', sa.SmallInteger(), nullable=True, comment='时间段ID（1-5，对应A-E时间段）'))


def downgrade() -> None:
    # 删除 time_slot_id 列
    op.drop_column('badminton_class_schedule', 'time_slot_id')