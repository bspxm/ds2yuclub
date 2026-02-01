#!/usr/bin/env python3
"""
创建学员列表视图
用于优化查询性能
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

ASYNC_DB_URL = "postgresql+asyncpg://postgres_yu:wAwafmNe4U8C@bspxm.myds.me:35432/ds2yuclub_db"

async def create_student_view():
    """创建学员列表视图"""
    print("开始创建学员视图...")

    engine = create_async_engine(ASYNC_DB_URL, echo=False)

    try:
        async with engine.begin() as conn:
            # 删除旧视图
            await conn.execute(text("DROP VIEW IF EXISTS view_badminton_student_list"))
            print("删除旧视图完成")

            # 创建新视图 - 使用 LEFT JOIN 关联家长信息
            await conn.execute(text("""
                CREATE VIEW view_badminton_student_list AS
                SELECT
                    s.id,
                    s.uuid,
                    s.name,
                    s.english_name,
                    s.gender,
                    s.birth_date,
                    s.height,
                    s.weight,
                    s.handedness,
                    s.join_date,
                    s.level,
                    s.group_name,
                    s.campus,
                    s.contact,
                    s.mobile,
                    s.description,
                    s.total_matches,
                    s.wins,
                    s.losses,
                    s.win_rate,
                    s.status,
                    s.created_time,
                    s.updated_time,
                    s.created_id,
                    s.updated_id,
                    -- 家长统计
                    COALESCE(ps.parent_count, 0) as parent_count,
                    -- 家长列表 (JSON数组)
                    COALESCE(ps.parents_json, '[]')::jsonb as parents_json
                FROM badminton_student s
                LEFT JOIN (
                    -- 统计家长信息
                    SELECT
                        student_id,
                        COUNT(*) as parent_count,
                        json_agg(json_build_object('id', u.id, 'name', u.name, 'relation_type', ps.relation_type)) as parents_json
                    FROM badminton_parent_student ps
                    LEFT JOIN sys_user u ON ps.parent_id = u.id
                    GROUP BY student_id
                ) ps ON s.id = ps.student_id
                ORDER BY s.id DESC
            """))
            print("创建新视图完成")

        print("✅ 学员视图创建成功！")

    except Exception as e:
        print(f"❌ 视图创建失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_student_view())