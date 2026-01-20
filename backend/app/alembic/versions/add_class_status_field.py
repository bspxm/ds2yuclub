"""add_class_status_field

Revision ID: add_class_status_field
Revises: make_session_price_nullable
Create Date: 2026-01-21 01:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_class_status_field'
down_revision: Union[str, None] = 'make_session_price_nullable'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 添加class_status字段
    op.add_column('badminton_class', sa.Column('class_status', sa.String(20), nullable=True, comment='班级状态'))
    
    # 更新现有数据
    op.execute("UPDATE badminton_class SET class_status = 'pending' WHERE class_status IS NULL")


def downgrade() -> None:
    # 删除class_status字段
    op.drop_column('badminton_class', 'class_status')