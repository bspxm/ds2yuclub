"""make_session_price_nullable

Revision ID: make_session_price_nullable
Revises: add_class_schedule
Create Date: 2026-01-21 00:51:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'make_session_price_nullable'
down_revision: Union[str, None] = 'add_class_schedule'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 将session_price字段改为可空
    op.alter_column('badminton_class', 'session_price',
                  existing_type=sa.Float(),
                  nullable=True)


def downgrade() -> None:
    # 将session_price字段改回必填
    op.alter_column('badminton_class', 'session_price',
                  existing_type=sa.Float(),
                  nullable=False)