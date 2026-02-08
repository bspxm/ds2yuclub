#!/usr/bin/env python3
"""
创建教练排课学员视图
用于优化学员列表查询性能
"""
import asyncio
import asyncpg
import os
import sys
from pathlib import Path

# 从.env.dev文件读取数据库配置
def load_env_file():
    """从.env.dev文件读取配置"""
    env_path = Path(__file__).parent.parent / "env" / ".env.dev"
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

async def create_view():
    """创建视图"""
    env_vars = load_env_file()
    
    # 数据库连接参数
    import re
    port_str = env_vars.get('DATABASE_PORT', '5432')
    port_clean = re.sub(r'[^0-9]', '', port_str)
    port = int(port_clean) if port_clean else 5432
    
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
        
        print("数据库连接成功，开始创建视图...")
        
        # 删除旧视图（如果存在）
        await conn.execute("DROP VIEW IF EXISTS view_badminton_coach_schedule_students")
        print("删除旧视图完成")
        
        # 创建新视图 - 包含学员列表的排课视图
        await conn.execute("""
            CREATE VIEW view_badminton_coach_schedule_students AS
            SELECT 
                s.id,
                s.uuid,
                s.class_id,
                s.schedule_date,
                s.day_of_week,
                s.time_slot_code,
                s.start_time,
                s.end_time,
                s.coach_id,
                s.schedule_status,
                s.location,
                s.topic,
                s.content_summary,
                s.notes,
                s.created_time,
                s.updated_time,
                -- 班级信息
                c.name as class_name,
                -- 教练信息
                u.name as coach_name,
                -- 学员列表（JSON聚合）
                COALESCE(
                    (
                        SELECT json_agg(
                            json_build_object(
                                'student_id', st.id,
                                'student_name', st.name,
                                'english_name', st.english_name,
                                'level', st.level,
                                'group_name', st.group_name,
                                'has_attended', CASE WHEN a.status = 'PRESENT' THEN true ELSE false END
                            )
                        )
                        FROM badminton_class_attendance a
                        JOIN badminton_student st ON a.student_id = st.id
                        WHERE a.schedule_id = s.id
                    ),
                    '[]'::json
                ) as students_json,
                -- 学员统计
                COALESCE(
                    (SELECT COUNT(*) FROM badminton_class_attendance WHERE schedule_id = s.id),
                    0
                ) as student_count,
                COALESCE(
                    (SELECT COUNT(*) FROM badminton_class_attendance WHERE schedule_id = s.id AND status = 'PRESENT'),
                    0
                ) as attendance_count
            FROM badminton_class_schedule s
            LEFT JOIN badminton_class c ON s.class_id = c.id
            LEFT JOIN sys_user u ON s.coach_id = u.id
        """)
        print("创建新视图完成")
        
        # 添加注释
        await conn.execute("COMMENT ON VIEW view_badminton_coach_schedule_students IS '教练排课学员视图，包含排课信息和学员列表（JSON格式）'")
        
        print("✅ 教练排课学员视图创建成功！")
        
        # 验证视图
        result = await conn.fetch("SELECT COUNT(*) as total FROM view_badminton_coach_schedule_students")
        print(f"视图包含 {result[0]['total']} 条记录")
        
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
    asyncio.run(create_view())