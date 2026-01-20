import psycopg2
from psycopg2 import sql

# 数据库配置
config = {
    'host': '192.168.1.11',
    'port': 35432,
    'user': 'postgres_yu',
    'password': 'wAwafmNe4U8C',
    'database': 'ds2yuclub_db'
}

try:
    # 连接数据库
    conn = psycopg2.connect(**config)
    conn.autocommit = True  # 自动提交
    cursor = conn.cursor()
    
    print("Database connection successful!")
    
    # 1. 删除 badminton_semester 表（如果存在）
    print("\n1. Dropping badminton_semester table...")
    cursor.execute("DROP TABLE IF EXISTS badminton_semester CASCADE;")
    print("   badminton_semester table dropped.")
    
    # 2. 删除旧的枚举类型
    print("\n2. Dropping old enum types...")
    cursor.execute("DROP TYPE IF EXISTS semestertypeenum;")
    print("   semestertypeenum dropped.")
    
    cursor.execute("DROP TYPE IF EXISTS semesterstatusenum;")
    print("   semesterstatusenum dropped.")
    
    # 3. 创建新的枚举类型（包含新值）
    print("\n3. Creating new enum types...")
    cursor.execute("CREATE TYPE semestertypeenum AS ENUM ('regular', 'summer', 'winter', 'wintersummer');")
    print("   semestertypeenum created with values: regular, summer, winter, wintersummer")
    
    cursor.execute("CREATE TYPE semesterstatusenum AS ENUM ('planning', 'in_progress', 'active', 'completed', 'settled', 'archived');")
    print("   semesterstatusenum created with values: planning, in_progress, active, completed, settled, archived")
    
    # 4. 创建 badminton_semester 表
    print("\n4. Creating badminton_semester table...")
    cursor.execute("""
        CREATE TABLE badminton_semester (
            name VARCHAR(64) NOT NULL,
            semester_type semestertypeenum NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            week_count SMALLINT NOT NULL DEFAULT 0,
            status semesterstatusenum NOT NULL DEFAULT 'planning',
            is_current BOOLEAN NOT NULL DEFAULT false,
            settlement_date DATE,
            carry_over_enabled BOOLEAN NOT NULL DEFAULT true,
            max_carry_over_sessions SMALLINT NOT NULL DEFAULT 5,
            description TEXT,
            id SERIAL PRIMARY KEY,
            uuid VARCHAR(64) NOT NULL UNIQUE,
            status_flag VARCHAR(10) NOT NULL DEFAULT '0',
            created_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            created_id INTEGER REFERENCES sys_user(id) ON UPDATE CASCADE ON DELETE SET NULL,
            updated_id INTEGER REFERENCES sys_user(id) ON UPDATE CASCADE ON DELETE SET NULL
        );
    """)
    print("   badminton_semester table created.")
    
    # 创建索引
    print("\n5. Creating indexes...")
    cursor.execute("CREATE INDEX ix_badminton_semester_id ON badminton_semester(id);")
    cursor.execute("CREATE INDEX ix_badminton_semester_created_time ON badminton_semester(created_time);")
    cursor.execute("CREATE INDEX ix_badminton_semester_updated_time ON badminton_semester(updated_time);")
    cursor.execute("CREATE INDEX ix_badminton_semester_status_flag ON badminton_semester(status_flag);")
    cursor.execute("CREATE INDEX ix_badminton_semester_uuid ON badminton_semester(uuid);")
    print("   Indexes created.")
    
    # 添加表注释
    cursor.execute("COMMENT ON TABLE badminton_semester IS '学期表';")
    
    print("\n✅ All operations completed successfully!")
    
    # 关闭连接
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()