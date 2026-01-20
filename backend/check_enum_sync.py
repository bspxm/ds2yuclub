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
    cursor = conn.cursor()
    
    print("Database connection successful!")
    
    # 检查 semestertypeenum 是否存在
    cursor.execute("""
        SELECT enumlabel 
        FROM pg_enum 
        WHERE enumtypid = 'semestertypeenum'::regtype 
        ORDER BY enumsortorder;
    """)
    semester_types = cursor.fetchall()
    print(f"\nsemestertypeenum: {[row[0] for row in semester_types]}")
    
    # 检查 semesterstatusenum 是否存在
    cursor.execute("""
        SELECT enumlabel 
        FROM pg_enum 
        WHERE enumtypid = 'semesterstatusenum'::regtype 
        ORDER BY enumsortorder;
    """)
    semester_statuses = cursor.fetchall()
    print(f"semesterstatusenum: {[row[0] for row in semester_statuses]}")
    
    # 检查 badminton_semester 表是否存在
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'badminton_semester'
        );
    """)
    table_exists = cursor.fetchone()[0]
    print(f"\nbadminton_semester table exists: {table_exists}")
    
    # 关闭连接
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")