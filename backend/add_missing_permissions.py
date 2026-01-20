#!/usr/bin/env python3
"""
添加羽毛球培训会员管理系统缺失的权限
使用方式: uv run python add_missing_permissions.py
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

async def add_missing_permissions():
    """添加缺失的权限"""
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
    
    print("正在连接数据库...")
    print(f"连接参数: host={db_config['host']}, port={db_config['port']}, database={db_config['database']}, user={db_config['user']}")
    
    try:
        # 连接数据库
        conn = await asyncpg.connect(**db_config)
        
        # 1. 查找学员管理菜单的ID
        print(f"\n查找学员管理菜单...")
        student_menu = await conn.fetchrow("""
            SELECT id FROM sys_menu 
            WHERE route_name = 'BadmintonStudent' AND type = 2
            LIMIT 1
        """)
        
        if not student_menu:
            print("错误: 未找到学员管理菜单，请先运行add_badminton_menu.py")
            await conn.close()
            sys.exit(1)
        
        student_parent_id = student_menu['id']
        print(f"找到学员管理菜单，ID: {student_parent_id}")
        
        # 2. 检查现有的权限
        existing_permissions = await conn.fetch("""
            SELECT name, permission FROM sys_menu 
            WHERE parent_id = $1 AND type = 3
            ORDER BY "order"
        """, student_parent_id)
        
        print(f"\n现有权限 ({len(existing_permissions)} 个):")
        for perm in existing_permissions:
            print(f"  - {perm['name']}: {perm['permission']}")
        
        # 3. 定义需要添加的权限
        missing_permissions = [
            {
                'name': '批量导入学员',
                'order': 7,
                'permission': 'module_badminton:student:import',
                'description': '批量导入学员信息'
            },
            {
                'name': '批量设置状态',
                'order': 8,
                'permission': 'module_badminton:student:batch_status',
                'description': '批量设置学员状态'
            }
        ]
        
        # 4. 添加缺失的权限
        added_count = 0
        for perm in missing_permissions:
            # 检查权限是否已存在
            exists = await conn.fetchval("""
                SELECT COUNT(*) FROM sys_menu 
                WHERE parent_id = $1 AND permission = $2
            """, student_parent_id, perm['permission'])
            
            if exists == 0:
                print(f"\n添加权限: {perm['name']} ({perm['permission']})")
                
                # 生成UUID（与add_badminton_menu.sql中的格式一致）
                import uuid
                import random
                import hashlib
                
                # 使用与SQL文件相同的UUID生成逻辑
                uuid_str = str(uuid.uuid4())
                
                await conn.execute("""
                    INSERT INTO sys_menu 
                    (name, type, "order", permission, icon, route_name, route_path, component_path, redirect, hidden, keep_alive, always_show, title, params, affix, parent_id, uuid, status, description, created_time, updated_time) 
                    VALUES 
                    ($1, 3, $2, $3, NULL, NULL, NULL, NULL, NULL, FALSE, TRUE, FALSE, $4, NULL, FALSE, $5, $6::uuid, '0', $7, NOW(), NOW())
                """, 
                perm['name'], perm['order'], perm['permission'], perm['name'], 
                student_parent_id, uuid_str, perm['description'])
                
                added_count += 1
                print(f"  ✅ 已添加")
            else:
                print(f"\n权限已存在: {perm['name']} ({perm['permission']})")
        
        # 5. 验证最终权限数量
        final_count = await conn.fetchval("""
            SELECT COUNT(*) FROM sys_menu 
            WHERE parent_id = $1 AND type = 3
        """, student_parent_id)
        
        print(f"\n{'='*50}")
        if added_count > 0:
            print(f"✅ 成功添加 {added_count} 个缺失的权限")
        else:
            print(f"✅ 所有权限已存在，无需添加")
        
        print(f"学员管理菜单现在共有 {final_count} 个操作权限")
        
        # 显示所有权限
        final_permissions = await conn.fetch("""
            SELECT name, permission, "order" FROM sys_menu 
            WHERE parent_id = $1 AND type = 3
            ORDER BY "order"
        """, student_parent_id)
        
        print("\n📋 当前权限列表:")
        for perm in final_permissions:
            print(f"  {perm['order']}. {perm['name']}: {perm['permission']}")
        
        await conn.close()
        
    except asyncpg.exceptions.PostgresError as e:
        print(f"❌ 数据库错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 执行错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(add_missing_permissions())