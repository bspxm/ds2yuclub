"""add CHAMPIONSHIP to tournamenttypeenum

Revision ID: ac28c8824c05
Revises: 642fc24c4f67
Create Date: 2026-04-08 00:08:20.278987

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ac28c8824c05"
down_revision: Union[str, None] = "642fc24c4f67"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE tournamenttypeenum ADD VALUE IF NOT EXISTS 'CHAMPIONSHIP'")


def downgrade() -> None:
    # PostgreSQL does not support removing enum values easily
    # Would need to recreate the enum type - skip downgrade for safety
    pass
