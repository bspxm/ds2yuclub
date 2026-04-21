#!/usr/bin/env python3
import asyncio
import os
from dotenv import load_dotenv
load_dotenv('/home/filter/myproject/ds2yuclub/backend/env/.env.dev')
import asyncpg

async def execute_sql():
    host = os.getenv('DATABASE_HOST')
    port = os.getenv('DATABASE_PORT')
    user = os.getenv('DATABASE_USER')
    password = os.getenv('DATABASE_PASSWORD')
    db_name = os.getenv('DATABASE_NAME')
    
    conn = await asyncpg.connect(
        host=host, port=port, user=user, password=password, database=db_name
    )
    
    sql = """
ALTER TABLE badminton_tournament_match 
ADD COLUMN IF NOT EXISTS prev_match1_id INTEGER,
ADD COLUMN IF NOT EXISTS prev_match2_id INTEGER,
ADD COLUMN IF NOT EXISTS next_match_id INTEGER;

CREATE INDEX IF NOT EXISTS idx_match_prev1 ON badminton_tournament_match(prev_match1_id);
CREATE INDEX IF NOT EXISTS idx_match_prev2 ON badminton_tournament_match(prev_match2_id);
CREATE INDEX IF NOT EXISTS idx_match_next ON badminton_tournament_match(next_match_id);
    """
    
    try:
        await conn.execute(sql)
        print("✅ 淘汰赛字段添加成功！")
        
        # 验证
        rows = await conn.fetch("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'badminton_tournament_match'
            AND column_name IN ('prev_match1_id', 'prev_match2_id', 'next_match_id')
        """)
        print(f"✅ 已添加字段: {[r['column_name'] for r in rows]}")
    except Exception as e:
        print(f"❌ 执行失败: {e}")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(execute_sql())
