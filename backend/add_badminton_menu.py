#!/usr/bin/env python3
"""
羽毛球培训会员管理系统菜单初始化脚本
使用方式: uv run python add_badminton_menu.py
"""

import asyncio
import asyncpg
import os
import sys
from pathlib import Path

# 从.env.dev文件读取数据库配置
def load_env_file():
    """从.env.dev文件读取配置"""
    env_path = Path(__file__).parent / "env" / ".env.dev"
    if not env_path.exists():
        print(f"错误: 环境文件不存在: {env_path}")
        sys.exit(1)
    
    env_vars = {}
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                # 分割键值对
                key, value = line.split('=', 1)
                key = key.strip()
                
                # 处理值中的注释（去除#及其后的内容）
                if '#' in value:
                    value = value.split('#')[0].strip()
                
                # 去除值两端的空白和引号
                value = value.strip().strip('"').strip("'")
                
                env_vars[key] = value
    
    return env_vars

async def execute_sql():
    """执行SQL文件"""
    env_vars = load_env_file()
    
    # 数据库连接参数
    # 处理端口号，确保是有效的整数
    port_str = env_vars.get('DATABASE_PORT', '5432')
    try:
        # 清理端口字符串：去除所有非数字字符
        import re
        port_clean = re.sub(r'[^0-9]', '', port_str)
        port = int(port_clean) if port_clean else 5432
    except (ValueError, TypeError):
        print(f"警告: 无法解析端口号 '{port_str}'，使用默认值 5432")
        port = 5432
    
    db_config = {
        'host': env_vars.get('DATABASE_HOST', 'localhost'),
        'port': port,
        'user': env_vars.get('DATABASE_USER', 'postgres'),
        'password': env_vars.get('DATABASE_PASSWORD', ''),
        'database': env_vars.get('DATABASE_NAME', 'fastapiadmin'),
    }
    
    # 读取SQL文件
    sql_path = Path(__file__).parent / "add_badminton_menu.sql"
    if not sql_path.exists():
        print(f"错误: SQL文件不存在: {sql_path}")
        sys.exit(1)
    
    with open(sql_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    print("正在连接数据库...")
    print(f"连接参数: host={db_config['host']}, port={db_config['port']}, database={db_config['database']}, user={db_config['user']}")
    
    try:
        # 连接数据库
        conn = await asyncpg.connect(**db_config)
        
        print("数据库连接成功，开始执行SQL...")
        
        # 执行SQL
        await conn.execute(sql_content)
        
        print("✅ 羽毛球培训会员管理系统菜单初始化完成！")
        
        # 验证插入的菜单项
        result = await conn.fetch("""
            SELECT 
                m1.name as level1_name,
                m2.name as level2_name,
                m2.route_path,
                m2.component_path,
                COUNT(m3.id) as permission_count
            FROM sys_menu m1
            LEFT JOIN sys_menu m2 ON m2.parent_id = m1.id AND m2.type = 2
            LEFT JOIN sys_menu m3 ON m3.parent_id = m2.id AND m3.type = 3
            WHERE m1.route_name = 'Badminton'
            GROUP BY m1.name, m2.name, m2.route_path, m2.component_path, m2."order"
            ORDER BY m2."order"
        """)
        
        if result:
            print("\n🗋 已添加的菜单项:")
            for row in result:
                if row['level2_name']:
                    print(f"  ├─ {row['level1_name']}")
                    print(f"  │  └─ {row['level2_name']} (路径: /badminton/{row['route_path']}, 组件: {row['component_path']})")
                    print(f"  │     └─ 包含 {row['permission_count']} 个操作权限")
                else:
                    print(f"  └─ {row['level1_name']} (一级菜单)")
        else:
            print("警告: 未找到羽毛球相关菜单，请检查SQL执行情况")
        
        await conn.close()
        
    except asyncpg.exceptions.PostgresError as e:
        print(f"❌ 数据库错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 执行错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(execute_sql())
