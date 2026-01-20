"""add_wintersummer_semester_type

Revision ID: add_wintersummer
Revises: f5e9d76b1c31
Create Date: 2026-01-20 22:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_wintersummer'
down_revision: Union[str, None] = 'ccd96fcb3dd5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 删除学期表（如果存在）
    op.drop_table('badminton_semester', if_exists=True)
    
    # 删除旧的枚举类型（如果存在）
    op.execute("DROP TYPE IF EXISTS semestertypeenum")
    op.execute("DROP TYPE IF EXISTS semesterstatusenum")
    
    # 创建学期类型枚举（包含 wintersummer）
    op.execute("CREATE TYPE semestertypeenum AS ENUM ('regular', 'summer', 'winter', 'wintersummer')")
    
    # 创建学期状态枚举（包含 in_progress）
    op.execute("CREATE TYPE semesterstatusenum AS ENUM ('planning', 'in_progress', 'active', 'completed', 'settled', 'archived')")
    
    # 创建学期表
    op.create_table('badminton_semester',
    sa.Column('name', sa.String(length=64), nullable=False, comment='学期名称'),
    sa.Column('semester_type', postgresql.ENUM('semestertypeenum', name='semestertypeenum'), nullable=False, comment='学期类型'),
    sa.Column('start_date', sa.Date(), nullable=False, comment='开始日期'),
    sa.Column('end_date', sa.Date(), nullable=False, comment='结束日期'),
    sa.Column('week_count', sa.SmallInteger(), nullable=False, server_default='0', comment='总周数'),
    sa.Column('status', postgresql.ENUM('semesterstatusenum', name='semesterstatusenum'), nullable=False, server_default='planning', comment='学期状态'),
    sa.Column('is_current', sa.Boolean(), nullable=False, server_default='false', comment='是否当前学期'),
    sa.Column('settlement_date', sa.Date(), nullable=True, comment='结算日期'),
    sa.Column('carry_over_enabled', sa.Boolean(), nullable=False, server_default='true', comment='允许课时结转'),
    sa.Column('max_carry_over_sessions', sa.SmallInteger(), nullable=False, server_default='5', comment='最大结转课时数'),
    sa.Column('description', sa.Text(), nullable=True, comment='学期描述'),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='主键ID'),
    sa.Column('uuid', sa.String(length=64), nullable=False, comment='UUID全局唯一标识'),
    sa.Column('is_available', sa.String(length=10), nullable=False, server_default='0', comment='是否启用(0:启用 1:禁用)'),
    sa.Column('created_time', sa.DateTime(), nullable=False, comment='创建时间'),
    sa.Column('updated_time', sa.DateTime(), nullable=False, comment='更新时间'),
    sa.Column('created_id', sa.Integer(), nullable=True, comment='创建人ID'),
    sa.Column('updated_id', sa.Integer(), nullable=True, comment='更新人ID'),
    sa.ForeignKeyConstraint(['created_id'], ['sys_user.id'], onupdate='CASCADE', ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['updated_id'], ['sys_user.id'], onupdate='CASCADE', ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
        comment='学期表'
    )
    op.create_index('ix_badminton_semester_id', 'badminton_semester', ['id'], unique=False)
    op.create_index('ix_badminton_semester_created_time', 'badminton_semester', ['created_time'], unique=False)
    op.create_index('ix_badminton_semester_updated_time', 'badminton_semester', ['updated_time'], unique=False)
    op.create_index('ix_badminton_semester_status', 'badminton_semester', ['status'], unique=False)
    op.create_index('ix_badminton_semester_uuid', 'badminton_semester', ['uuid'], unique=True)


def downgrade() -> None:
    # 删除学期表
    op.drop_table('badminton_semester')
    
    # 删除学期状态枚举
    op.execute("DROP TYPE IF EXISTS semesterstatusenum")
    
    # 删除学期类型枚举
    op.execute("DROP TYPE IF EXISTS semestertypeenum")