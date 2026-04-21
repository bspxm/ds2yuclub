"""make_player_ids_nullable

Revision ID: df85d85d9bed
Revises: e5f2a6fd70bc
Create Date: 2026-04-06 02:29:14.632137

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "df85d85d9bed"
down_revision: Union[str, None] = "e5f2a6fd70bc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 修改 player1_id 为可空
    op.alter_column(
        "badminton_tournament_match",
        "player1_id",
        existing_type=sa.INTEGER(),
        nullable=True,
    )

    # 修改 player2_id 为可空
    op.alter_column(
        "badminton_tournament_match",
        "player2_id",
        existing_type=sa.INTEGER(),
        nullable=True,
    )


def downgrade() -> None:
    # 恢复为不可空
    op.alter_column(
        "badminton_tournament_match",
        "player1_id",
        existing_type=sa.INTEGER(),
        nullable=False,
    )

    op.alter_column(
        "badminton_tournament_match",
        "player2_id",
        existing_type=sa.INTEGER(),
        nullable=False,
    )
