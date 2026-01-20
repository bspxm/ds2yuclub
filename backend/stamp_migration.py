import psycopg2

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
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("Database connection successful!")
    
    # 检查当前迁移状态
    print("\nCurrent migration status:")
    cursor.execute("SELECT version_num FROM alembic_version;")
    current_version = cursor.fetchone()
    print(f"Current version: {current_version[0] if current_version else 'None'}")
    
    # 更新迁移版本
    print("\nUpdating migration version to 'add_wintersummer'...")
    cursor.execute("UPDATE alembic_version SET version_num = 'add_wintersummer';")
    print("Migration version updated successfully!")
    
    # 验证更新
    cursor.execute("SELECT version_num FROM alembic_version;")
    updated_version = cursor.fetchone()
    print(f"New version: {updated_version[0]}")
    
    print("\n✅ Migration stamped successfully!")
    
    # 关闭连接
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()