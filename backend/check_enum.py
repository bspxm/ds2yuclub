import asyncio
from sqlalchemy import text
from app.core.database import async_engine


async def check_enums():
    async with async_engine.begin() as conn:
        # 检查 semestertypeenum 是否存在
        result = await conn.execute(text("""
            SELECT enumlabel 
            FROM pg_enum 
            WHERE enumtypid = 'semestertypeenum'::regtype 
            ORDER BY enumsortorder;
        """))
        semester_types = result.fetchall()
        print("semestertypeenum:", [row[0] for row in semester_types])
        
        # 检查 semesterstatusenum 是否存在
        result = await conn.execute(text("""
            SELECT enumlabel 
            FROM pg_enum 
            WHERE enumtypid = 'semesterstatusenum'::regtype 
            ORDER BY enumsortorder;
        """))
        semester_statuses = result.fetchall()
        print("semesterstatusenum:", [row[0] for row in semester_statuses])


if __name__ == "__main__":
    asyncio.run(check_enums())