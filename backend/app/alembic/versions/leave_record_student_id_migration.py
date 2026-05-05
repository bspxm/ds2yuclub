"""leave_record: student_course_id -> student_id, drop course tables

Revision ID: leave_record_student_id
Revises: 95a28c04c8ae
Create Date: 2026-05-05
"""
from alembic import op
import sqlalchemy as sa

revision = 'leave_record_student_id'
down_revision = '95a28c04c8ae'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # 检查 student_course_id 列是否存在
    result = conn.execute(sa.text("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'badminton_leave_record' AND column_name = 'student_course_id'
    """))
    has_old_column = result.fetchone() is not None

    if has_old_column:
        # 添加新列
        conn.execute(sa.text("ALTER TABLE badminton_leave_record ADD COLUMN IF NOT EXISTS student_id INTEGER"))

        # 检查 badminton_student_course 表是否存在，尝试迁移数据
        result = conn.execute(sa.text("""
            SELECT table_name FROM information_schema.tables
            WHERE table_name = 'badminton_student_course'
        """))
        if result.fetchone() is not None:
            conn.execute(sa.text("""
                UPDATE badminton_leave_record
                SET student_id = sc.student_id
                FROM badminton_student_course sc
                WHERE badminton_leave_record.student_course_id = sc.id
            """))

        # 删除旧外键和旧列
        conn.execute(sa.text(
            "ALTER TABLE badminton_leave_record DROP CONSTRAINT IF EXISTS badminton_leave_record_student_course_id_fkey"
        ))
        conn.execute(sa.text("ALTER TABLE badminton_leave_record DROP COLUMN student_course_id"))
        conn.execute(sa.text("ALTER TABLE badminton_leave_record ALTER COLUMN student_id SET NOT NULL"))
        conn.execute(sa.text("""
            ALTER TABLE badminton_leave_record ADD CONSTRAINT badminton_leave_record_student_id_fkey
            FOREIGN KEY (student_id) REFERENCES badminton_student(id) ON DELETE CASCADE ON UPDATE CASCADE
        """))
        conn.execute(sa.text(
            "CREATE INDEX IF NOT EXISTS ix_badminton_leave_record_student_id ON badminton_leave_record (student_id)"
        ))

    # 删除旧的课程相关表
    conn.execute(sa.text("DROP TABLE IF EXISTS badminton_student_course CASCADE"))
    conn.execute(sa.text("DROP TABLE IF EXISTS badminton_course CASCADE"))

    # 删除课程菜单及权限
    conn.execute(sa.text(
        "DELETE FROM sys_menu WHERE permission LIKE 'module_badminton:course:%' AND type = 3"
    ))
    conn.execute(sa.text("DELETE FROM sys_menu WHERE route_name = 'BadmintonCourse'"))
    conn.execute(sa.text("""
        UPDATE sys_menu SET description = '教学管理：排课、考勤、评估、分组',
                            redirect = '/Badminton/schedule'
        WHERE route_name = 'BadmintonTeaching'
    """))


def downgrade() -> None:
    pass
