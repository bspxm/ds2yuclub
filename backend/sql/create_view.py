#!/usr/bin/env python3
"""
在数据库中创建排课记录列表视图
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text

ASYNC_DB_URL = "postgresql+asyncpg://postgres_yu:wAwafmNe4U8C@bspxm.myds.me:35432/ds2yuclub_db"

async def create_view():
    """创建视图"""
    print("开始创建视图...")
    
    engine = create_async_engine(ASYNC_DB_URL, echo=False)
    
    try:
        async with engine.begin() as conn:
            # 删除旧视图
            await conn.execute(text("DROP VIEW IF EXISTS view_badminton_class_schedule_list"))
            print("删除旧视图完成")
            
            # 创建新视图
            await conn.execute(text("""
                CREATE VIEW view_badminton_class_schedule_list AS
                SELECT 
                    s.id,
                    s.uuid,
                    s.class_id,
                    s.schedule_date,
                    s.day_of_week,
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
                    c.name as class_ref_name,
                    c.semester_id as class_ref_semester_id,
                    -- 教练信息
                    u.id as coach_user_id,
                    u.name as coach_user_name
                FROM badminton_class_schedule s
                LEFT JOIN badminton_class c ON s.class_id = c.id
                LEFT JOIN sys_user u ON s.coach_id = u.id
            """))
            print("创建新视图完成")
        
        print("✅ 视图创建成功！")
        
    except Exception as e:
        print(f"❌ 视图创建失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_view())