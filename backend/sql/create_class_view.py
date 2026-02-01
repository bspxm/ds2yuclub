#!/usr/bin/env python3
"""
在数据库中创建班级列表视图
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

ASYNC_DB_URL = "postgresql+asyncpg://postgres_yu:wAwafmNe4U8C@bspxm.myds.me:35432/ds2yuclub_db"

async def create_view():
    """创建视图"""
    print("开始创建班级视图...")
    
    engine = create_async_engine(ASYNC_DB_URL, echo=False)
    
    try:
        async with engine.begin() as conn:
            # 删除旧视图
            await conn.execute(text("DROP VIEW IF EXISTS view_badminton_class_list"))
            print("删除旧视图完成")
            
            # 创建新视图
            await conn.execute(text("""
                CREATE VIEW view_badminton_class_list AS
                SELECT 
                    c.id,
                    c.uuid,
                    c.semester_id,
                    c.name,
                    c.class_type,
                    c.coach_id,
                    c.total_sessions,
                    c.sessions_per_week,
                    c.session_duration,
                    c.session_price,
                    c.max_students,
                    c.min_students,
                    c.current_students,
                    c.start_date,
                    c.end_date,
                    c.weekly_schedule,
                    c.time_slots_json,
                    c.location,
                    c.class_status,
                    c.is_active,
                    c.enrollment_open,
                    c.fee_per_session,
                    c.notes,
                    c.description,
                    c.created_time,
                    c.updated_time,
                    c.created_id,
                    c.updated_id,
                    -- 学期信息
                    sem.id as semester_ref_id,
                    sem.name as semester_name,
                    sem.semester_type as semester_type,
                    -- 教练信息
                    u.id as coach_user_id,
                    u.name as coach_user_name
                FROM badminton_class c
                LEFT JOIN badminton_semester sem ON c.semester_id = sem.id
                LEFT JOIN sys_user u ON c.coach_id = u.id
            """))
            print("创建新视图完成")
        
        print("✅ 班级视图创建成功！")
        
    except Exception as e:
        print(f"❌ 视图创建失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_view())