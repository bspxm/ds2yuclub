#!/usr/bin/env python3
"""
在数据库中创建购买记录列表视图
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

ASYNC_DB_URL = "postgresql+asyncpg://postgres_yu:wAwafmNe4U8C@bspxm.myds.me:35432/ds2yuclub_db"

async def create_view():
    """创建视图"""
    print("开始创建购买记录视图...")
    
    engine = create_async_engine(ASYNC_DB_URL, echo=False)
    
    try:
        async with engine.begin() as conn:
            # 删除旧视图
            await conn.execute(text("DROP VIEW IF EXISTS view_badminton_purchase_list"))
            print("删除旧视图完成")
            
            # 创建新视图
            await conn.execute(text("""
                CREATE VIEW view_badminton_purchase_list AS
                SELECT 
                    p.id,
                    p.uuid,
                    p.student_id,
                    p.class_id,
                    p.semester_id,
                    p.purchase_date,
                    p.total_sessions,
                    p.used_sessions,
                    p.remaining_sessions,
                    p.carry_over_sessions,
                    p.credit_sessions,
                    p.valid_from,
                    p.valid_until,
                    p.status,
                    p.is_settled,
                    p.settlement_date,
                    p.original_price,
                    p.actual_price,
                    p.discount_rate,
                    p.purchase_notes,
                    p.selected_time_slots,
                    p.description,
                    p.created_time,
                    p.updated_time,
                    p.created_id,
                    p.updated_id,
                    -- 学员信息
                    s.id as student_ref_id,
                    s.name as student_name,
                    s.gender as student_gender,
                    s.mobile as student_mobile,
                    -- 班级信息
                    c.id as class_ref_id,
                    c.name as class_name,
                    c.class_type as class_type,
                    c.coach_id as class_coach_id,
                    -- 学期信息
                    sem.id as semester_ref_id,
                    sem.name as semester_name,
                    sem.semester_type as semester_type,
                    -- 教练信息
                    u.id as coach_user_id,
                    u.name as coach_user_name
                FROM badminton_purchase p
                LEFT JOIN badminton_student s ON p.student_id = s.id
                LEFT JOIN badminton_class c ON p.class_id = c.id
                LEFT JOIN badminton_semester sem ON p.semester_id = sem.id
                LEFT JOIN sys_user u ON c.coach_id = u.id
            """))
            print("创建新视图完成")
        
        print("✅ 购买记录视图创建成功！")
        
    except Exception as e:
        print(f"❌ 视图创建失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_view())