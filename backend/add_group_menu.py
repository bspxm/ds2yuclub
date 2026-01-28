#!/usr/bin/env python3
"""
能力分组管理菜单初始化脚本
使用方式: uv run python add_group_menu.py
"""

import asyncio
import asyncpg
import os
import sys
from pathlib import Path
import re

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
    sql_path = Path(__file__).parent / "add_group_menu.sql"
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
        
        print("✅ 能力分组管理菜单初始化完成！")
        
        # 验证插入的菜单项
        result = await conn.fetch("""
            SELECT 
                m.name,
                m.route_path,
                m.component_path,
                m.permission
            FROM sys_menu m
            WHERE m.route_name = 'BadmintonGroup'
        """)
        
        if result:
            print("\n🗋 已添加的能力分组管理菜单:")
            for row in result:
                print(f"  ├─ {row['name']}")
                print(f"  │  ├─ 路径: /badminton/{row['route_path']}")
                print(f"  │  ├─ 组件: {row['component_path']}")
                print(f"  │  └─ 权限: {row['permission']}")
        else:
            print("警告: 未找到能力分组管理菜单，请检查SQL执行情况")
        
        # 显示所有操作权限
        permissions = await conn.fetch("""
            SELECT m.name, m.permission
            FROM sys_menu m
            WHERE m.parent_id = (
                SELECT id FROM sys_menu WHERE route_name = 'BadmintonGroup'
            ) AND m.type = 3
            ORDER BY m."order"
        """)
        
        if permissions:
            print("\n🔐 已添加的操作权限:")
            for perm in permissions:
                print(f"  ├─ {perm['name']}: {perm['permission']}")
        
        await conn.close()
        
    except asyncpg.exceptions.PostgresError as e:
        print(f"❌ 数据库错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 执行错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(execute_sql())
