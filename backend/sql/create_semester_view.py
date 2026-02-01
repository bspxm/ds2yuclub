#!/usr/bin/env python3
"""
创建学期列表视图
用于优化查询性能
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

ASYNC_DB_URL = "postgresql+asyncpg://postgres_yu:wAwafmNe4U8C@bspxm.myds.me:35432/ds2yuclub_db"

async def create_semester_view():
    """创建学期列表视图"""
    print("开始创建学期视图...")
    
    engine = create_async_engine(ASYNC_DB_URL, echo=False)
    
    try:
        async with engine.begin() as conn:
            # 删除旧视图
            await conn.execute(text("DROP VIEW IF EXISTS view_badminton_semester_list"))
            print("删除旧视图完成")
            
            # 创建新视图
            await conn.execute(text("""
                CREATE VIEW view_badminton_semester_list AS
                SELECT 
                    s.id,
                    s.uuid,
                    s.name,
                    s.semester_type,
                    s.start_date,
                    s.end_date,
                    s.week_count,
                    s.status,
                    s.is_current,
                    s.settlement_date,
                    s.carry_over_enabled,
                    s.max_carry_over_sessions,
                    s.description,
                    s.status_flag,
                    s.created_time,
                    s.updated_time,
                    s.created_id,
                    s.updated_id,
                    -- 统计字段（预留）
                    NULL as class_count,
                    NULL as purchase_count
                FROM badminton_semester s
                ORDER BY s.start_date DESC
            """))
            print("创建新视图完成")
        
        print("✅ 学期视图创建成功！")
        
    except Exception as e:
        print(f"❌ 视图创建失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_semester_view())