"""make_time_fields_nullable

Revision ID: make_time_fields_nullable
Revises: f7f80e0ada53
Create Date: 2026-01-29 03:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'make_time_fields_nullable'
down_revision: Union[str, None] = 'f7f80e0ada53'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 使时间字段允许NULL，用于V2版本的排课记录
    op.alter_column('badminton_class_schedule', 'start_time',
               existing_type=sa.TIME(),
               nullable=True,
               existing_comment='开始时间（V1版本使用，V2版本从配置获取）')
    op.alter_column('badminton_class_schedule', 'end_time',
               existing_type=sa.TIME(),
               nullable=True,
               existing_comment='结束时间（V1版本使用，V2版本从配置获取）')
    op.alter_column('badminton_class_schedule', 'duration_minutes',
               existing_type=sa.SMALLINT(),
               nullable=True,
               existing_comment='课时分钟数（V1版本使用，V2版本从配置获取）')


def downgrade() -> None:
    # 回滚：恢复NOT NULL约束
    op.alter_column('badminton_class_schedule', 'duration_minutes',
               existing_type=sa.SMALLINT(),
               nullable=False,
               existing_comment='课时分钟数（V1版本使用，V2版本从配置获取）')
    op.alter_column('badminton_class_schedule', 'end_time',
               existing_type=sa.TIME(),
               nullable=False,
               existing_comment='结束时间（V1版本使用，V2版本从配置获取）')
    op.alter_column('badminton_class_schedule', 'start_time',
               existing_type=sa.TIME(),
               nullable=False,
               existing_comment='开始时间（V1版本使用，V2版本从配置获取）')