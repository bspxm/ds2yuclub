#!/usr/bin/env python3
"""
测试分组API并检查数据库中的数据
"""

import asyncio
import asyncpg
import re
from pathlib import Path
import sys
import json

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
                key, value = line.split('=', 1)
                key = key.strip()
                if '#' in value:
                    value = value.split('#')[0].strip()
                value = value.strip().strip('"').strip("'")
                env_vars[key] = value

    return env_vars

async def check_database():
    """检查数据库中的分组数据"""
    env_vars = load_env_file()

    # 数据库连接参数
    port_str = env_vars.get('DATABASE_PORT', '5432')
    try:
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
        conn = await asyncpg.connect(**db_config)
        print("数据库连接成功\n")

        # 检查分组表是否存在
        tables = await conn.fetch("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = 'badminton_group'
        """)

        if not tables:
            print("❌ 分组表 badminton_group 不存在")
            return

        print("✅ 分组表 badminton_group 存在\n")

        # 查询分组数据
        groups = await conn.fetch("""
            SELECT id, name, description, status, created_time
            FROM badminton_group
            ORDER BY id
        """)

        if groups:
            print(f"📊 数据库中有 {len(groups)} 条分组记录:\n")
            for group in groups:
                print(f"  ID: {group['id']}")
                print(f"  名称: {group['name']}")
                print(f"  描述: {group['description'] or '无'}")
                print(f"  状态: {group['status']}")
                print(f"  创建时间: {group['created_time']}")
                print()

            # 查询关联的教练数量
            for group in groups:
                coach_count = await conn.fetchval("""
                    SELECT COUNT(*)
                    FROM badminton_group_coach
                    WHERE group_id = $1
                """, group['id'])

                student_count = await conn.fetchval("""
                    SELECT COUNT(*)
                    FROM badminton_group_student
                    WHERE group_id = $1
                """, group['id'])

                print(f"  {group['name']} - 教练: {coach_count} 人, 学员: {student_count} 人")

        else:
            print("❌ 数据库中没有分组数据")
            print("\n提示: 请先使用前端页面创建分组数据")

        # 检查菜单配置
        print("\n🔍 检查菜单配置...")
        menu = await conn.fetch("""
            SELECT route_path, component_path, permission, status
            FROM sys_menu
            WHERE route_name = 'BadmintonGroup'
        """)

        if menu:
            menu = menu[0]
            print(f"  路由路径: {menu['route_path']}")
            print(f"  组件路径: {menu['component_path']}")
            print(f"  权限标识: {menu['permission']}")
            print(f"  菜单状态: {menu['status']}")

            # 检查用户是否有权限
            print("\n🔍 检查管理员权限...")
            user_perms = await conn.fetch("""
                SELECT DISTINCT m.permission
                FROM sys_user u
                JOIN sys_user_role ur ON u.id = ur.user_id
                JOIN sys_role r ON ur.role_id = r.id
                JOIN sys_role_menu rm ON r.id = rm.role_id
                JOIN sys_menu m ON rm.menu_id = m.id
                WHERE u.username = 'admin'
                AND m.permission LIKE 'module_badminton:group%'
            """)

            if user_perms:
                print("  ✅ 管理员具有以下权限:")
                for perm in user_perms:
                    print(f"    - {perm['permission']}")
            else:
                print("  ❌ 管理员没有能力分组相关权限")

        await conn.close()

    except asyncpg.exceptions.PostgresError as e:
        print(f"❌ 数据库错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 执行错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(check_database())
