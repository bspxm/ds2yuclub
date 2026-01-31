"""merge_multiple_heads

Revision ID: d98ed3570aef
Revises: add_badminton_time_slot, add_sessions_per_week_to_class, add_time_slot_id, make_time_fields_nullable
Create Date: 2026-01-31 20:44:59.541622

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd98ed3570aef'
down_revision: Union[str, None] = ('add_badminton_time_slot', 'add_sessions_per_week_to_class', 'add_time_slot_id', 'make_time_fields_nullable')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
