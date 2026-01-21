"""重命名学员表字段：emergency_contact→contact, emergency_phone→mobile

Revision ID: 9f16c8b786e6
Revises: add_class_status_field
Create Date: 2026-01-21 23:23:06.890078

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f16c8b786e6'
down_revision: Union[str, None] = 'add_class_status_field'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 重命名 emergency_contact 为 contact
    op.alter_column('badminton_student', 'emergency_contact', new_column_name='contact')
    
    # 重命名 emergency_phone 为 mobile
    op.alter_column('badminton_student', 'emergency_phone', new_column_name='mobile')


def downgrade() -> None:
    # 回滚：重命名 contact 为 emergency_contact
    op.alter_column('badminton_student', 'contact', new_column_name='emergency_contact')
    
    # 回滚：重命名 mobile 为 emergency_phone
    op.alter_column('badminton_student', 'mobile', new_column_name='emergency_phone')
