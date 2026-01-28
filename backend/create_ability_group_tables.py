"""
手动创建能力分组管理相关表的脚本

执行方式：
python3 create_ability_group_tables.py
"""

from sqlalchemy import text
from app.core.database import db_session


def create_tables():
    """创建能力分组管理相关表"""
    session = db_session()
    try:
        try:
            # 创建分组主表
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS badminton_group (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(64) NOT NULL,
                    description TEXT,
                    created_id INTEGER,
                    updated_id INTEGER,
                    created_time TIMESTAMP,
                    updated_time TIMESTAMP,
                    CONSTRAINT badminton_group_name_key UNIQUE (name)
                )
            """))
            session.execute(text("""
                COMMENT ON TABLE badminton_group IS '能力分组表'
            """))
            session.execute(text("""
                COMMENT ON COLUMN badminton_group.name IS '分组名称'
            """))
            session.execute(text("""
                COMMENT ON COLUMN badminton_group.description IS '备注说明'
            """))

            # 创建分组-教练关联表
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS badminton_group_coach (
                    group_id INTEGER NOT NULL,
                    coach_id INTEGER NOT NULL,
                    PRIMARY KEY (group_id, coach_id),
                    CONSTRAINT fk_group_coach_group FOREIGN KEY (group_id)
                        REFERENCES badminton_group (id) ON DELETE CASCADE ON UPDATE CASCADE,
                    CONSTRAINT fk_group_coach_user FOREIGN KEY (coach_id)
                        REFERENCES sys_user (id) ON DELETE CASCADE ON UPDATE CASCADE
                )
            """))
            session.execute(text("""
                COMMENT ON TABLE badminton_group_coach IS '分组-教练关联表'
            """))
            session.execute(text("""
                COMMENT ON COLUMN badminton_group_coach.group_id IS '分组ID'
            """))
            session.execute(text("""
                COMMENT ON COLUMN badminton_group_coach.coach_id IS '教练用户ID'
            """))

            # 创建分组-学员关联表
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS badminton_group_student (
                    group_id INTEGER NOT NULL,
                    student_id INTEGER NOT NULL,
                    PRIMARY KEY (group_id, student_id),
                    CONSTRAINT fk_group_student_group FOREIGN KEY (group_id)
                        REFERENCES badminton_group (id) ON DELETE CASCADE ON UPDATE CASCADE,
                    CONSTRAINT fk_group_student_student FOREIGN KEY (student_id)
                        REFERENCES badminton_student (id) ON DELETE CASCADE ON UPDATE CASCADE
                )
            """))
            session.execute(text("""
                COMMENT ON TABLE badminton_group_student IS '分组-学员关联表'
            """))
            session.execute(text("""
                COMMENT ON COLUMN badminton_group_student.group_id IS '分组ID'
            """))
            session.execute(text("""
                COMMENT ON COLUMN badminton_group_student.student_id IS '学员ID'
            """))

            # 创建索引
            session.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_badminton_group_name ON badminton_group (name)
            """))

            session.commit()
            print("✅ 能力分组管理表创建成功！")
            print("   - badminton_group (能力分组表)")
            print("   - badminton_group_coach (分组-教练关联表)")
            print("   - badminton_group_student (分组-学员关联表)")

        except Exception as e:
            session.rollback()
            print(f"❌ 创建表失败: {e}")
            raise
    finally:
        session.close()


if __name__ == "__main__":
    create_tables()