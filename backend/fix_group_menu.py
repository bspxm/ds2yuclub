#!/usr/bin/env python3
"""
修复能力分组管理菜单路由路径
"""

import asyncio
import asyncpg
import re
from pathlib import Path
import sys

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
                key, value = line.split('=', 1)
                key = key.strip()
                if '#' in value:
                    value = value.split('#')[0].strip()
                value = value.strip().strip('"').strip("'")
                env_vars[key] = value

    return env_vars

async def fix_menu_route():
    """修复菜单路由路径"""
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
        print("数据库连接成功")

        # 查询当前菜单配置
        result = await conn.fetch("""
            SELECT id, name, route_path, route_name, component_path, parent_id
            FROM sys_menu
            WHERE route_name = 'BadmintonGroup'
        """)

        if result:
            row = result[0]
            print(f"\n当前菜单配置:")
            print(f"  ID: {row['id']}")
            print(f"  名称: {row['name']}")
            print(f"  路由路径: {row['route_path']}")
            print(f"  路由名称: {row['route_name']}")
            print(f"  组件路径: {row['component_path']}")
            print(f"  父菜单ID: {row['parent_id']}")

            # 修复路由路径
            correct_path = "group"
            if row['route_path'] != correct_path:
                print(f"\n检测到路由路径错误: {row['route_path']}")
                print(f"正在修正为: {correct_path}")

                await conn.execute("""
                    UPDATE sys_menu
                    SET route_path = $1
                    WHERE route_name = 'BadmintonGroup'
                """, correct_path)

                print("✅ 路由路径修正完成！")
            else:
                print("\n✅ 路由路径正确，无需修正")

            # 验证修正结果
            updated = await conn.fetchval("""
                SELECT route_path
                FROM sys_menu
                WHERE route_name = 'BadmintonGroup'
            """)

            print(f"\n修正后的路由路径: {updated}")
        else:
            print("\n❌ 未找到能力分组管理菜单")

        await conn.close()

    except asyncpg.exceptions.PostgresError as e:
        print(f"❌ 数据库错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 执行错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(fix_menu_route())