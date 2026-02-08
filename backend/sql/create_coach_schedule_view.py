#!/usr/bin/env python3
"""
创建教练排课视图
用于优化教练排课查询性能
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
        await conn.execute("DROP VIEW IF EXISTS view_badminton_coach_schedule")
        print("删除旧视图完成")
        
        # 创建新视图
        await conn.execute("""
            CREATE VIEW view_badminton_coach_schedule AS
            SELECT 
                s.id,
                s.uuid,
                s.class_id,
                s.schedule_date,
                s.day_of_week,
                s.time_slot_id,
                s.time_slot_code,
                s.time_slots_json,
                s.start_time,
                s.end_time,
                s.duration_minutes,
                s.schedule_type,
                s.schedule_status,
                s.coach_id,
                s.coach_confirmed,
                s.coach_confirm_at,
                s.court_number,
                s.location,
                s.topic,
                s.content_summary,
                s.training_focus,
                s.equipment_needed,
                s.is_published,
                s.published_at,
                s.is_auto_generated,
                s.original_schedule_id,
                s.makeup_for_schedule_id,
                s.notes,
                s.status,
                s.description,
                s.created_time,
                s.updated_time,
                s.created_id,
                s.updated_id,
                -- 班级信息
                c.id as class_ref_id,
                c.name as class_name,
                c.semester_id,
                -- 教练信息
                u.id as coach_user_id,
                u.name as coach_name,
                -- 学员统计
                COALESCE(att.attendance_count, 0) as attendance_count,
                COALESCE(att.absent_count, 0) as absent_count,
                COALESCE(att.leave_count, 0) as leave_count
            FROM badminton_class_schedule s
            LEFT JOIN badminton_class c ON s.class_id = c.id
            LEFT JOIN sys_user u ON s.coach_id = u.id
            LEFT JOIN (
                -- 统计每个排课的考勤数据
                SELECT 
                    schedule_id,
                    COUNT(*) as attendance_count,
                    COUNT(*) FILTER (WHERE status = 'ABSENT') as absent_count,
                    COUNT(*) FILTER (WHERE status = 'LEAVE') as leave_count
                FROM badminton_class_attendance
                GROUP BY schedule_id
            ) att ON s.id = att.schedule_id
        """)
        print("创建新视图完成")
        
        # 添加注释
        await conn.execute("COMMENT ON VIEW view_badminton_coach_schedule IS '教练排课视图，包含排课、班级、教练和考勤统计信息'")
        
        print("✅ 教练排课视图创建成功！")
        
        # 验证视图
        result = await conn.fetch("SELECT COUNT(*) as total FROM view_badminton_coach_schedule")
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