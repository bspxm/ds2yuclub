#!/usr/bin/env python3
"""
创建分组列表视图
用于优化查询性能
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

ASYNC_DB_URL = "postgresql+asyncpg://postgres_yu:wAwafmNe4U8C@bspxm.myds.me:35432/ds2yuclub_db"

async def create_group_view():
    """创建分组列表视图"""
    print("开始创建分组视图...")
    
    engine = create_async_engine(ASYNC_DB_URL, echo=False)
    
    try:
        async with engine.begin() as conn:
            # 删除旧视图
            await conn.execute(text("DROP VIEW IF EXISTS view_badminton_group_list"))
            print("删除旧视图完成")
            
            # 创建新视图 - 使用 JSON 聚合教练和学员信息
            await conn.execute(text("""
                CREATE VIEW view_badminton_group_list AS
                SELECT 
                    g.id,
                    g.uuid,
                    g.name,
                    g.description,
                    g.created_time,
                    g.updated_time,
                    g.created_id,
                    g.updated_id,
                    -- 教练统计
                    COALESCE(gc.coach_count, 0) as coach_count,
                    -- 学员统计
                    COALESCE(gs.student_count, 0) as student_count,
                    -- 教练列表 (JSON数组)
                    COALESCE(gc.coaches_json, '[]')::jsonb as coaches_json,
                    -- 学员列表 (JSON数组)
                    COALESCE(gs.students_json, '[]')::jsonb as students_json
                FROM badminton_group g
                LEFT JOIN (
                    -- 统计教练信息
                    SELECT 
                        group_id,
                        COUNT(*) as coach_count,
                        json_agg(json_build_object('id', u.id, 'name', u.name)) as coaches_json
                    FROM badminton_group_coach
                    LEFT JOIN sys_user u ON badminton_group_coach.coach_id = u.id
                    GROUP BY group_id
                ) gc ON g.id = gc.group_id
                LEFT JOIN (
                    -- 统计学员信息
                    SELECT 
                        group_id,
                        COUNT(*) as student_count,
                        json_agg(json_build_object('id', s.id, 'name', s.name)) as students_json
                    FROM badminton_group_student
                    LEFT JOIN badminton_student s ON badminton_group_student.student_id = s.id
                    GROUP BY group_id
                ) gs ON g.id = gs.group_id
                ORDER BY g.id DESC
            """))
            print("创建新视图完成")
        
        print("✅ 分组视图创建成功！")
        
    except Exception as e:
        print(f"❌ 视图创建失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_group_view())