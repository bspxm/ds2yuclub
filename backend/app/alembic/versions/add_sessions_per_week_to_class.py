"""add_sessions_per_week_to_class

Revision ID: add_sessions_per_week_to_class
Revises: add_class_status_field
Create Date: 2026-01-31 20:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_sessions_per_week_to_class'
down_revision: Union[str, None] = 'add_class_status_field'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 添加sessions_per_week字段
    op.add_column('badminton_class', sa.Column('sessions_per_week', sa.SmallInteger, nullable=True, comment='每周课次'))


def downgrade() -> None:
    # 删除sessions_per_week字段
    op.drop_column('badminton_class', 'sessions_per_week')