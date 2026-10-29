import pytest
from sqlalchemy import text

from app.database import engine, init_db


@pytest.mark.asyncio
async def test_database_initialization():
    await init_db()
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT count(*) FROM category"))
        count = res.scalar()
        assert count == 5, f"Expected 5 categories, got {count}"
