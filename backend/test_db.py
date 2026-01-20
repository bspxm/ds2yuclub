import asyncio
from app.core.database import async_engine


async def test_db():
    try:
        async with async_engine.connect() as conn:
            print('Database connection successful')
            return True
    except Exception as e:
        print(f'Database connection failed: {e}')
        return False


if __name__ == "__main__":
    result = asyncio.run(test_db())
    print(f"Result: {result}")