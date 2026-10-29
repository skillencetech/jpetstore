import os
from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initializes tables and seeds data if not already populated."""
    async with engine.begin() as conn:
        res = await conn.execute(text("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='category'"))
        table_exists = (res.scalar() or 0) > 0
        if not table_exists:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            schema_path = os.path.join(base_dir, "sql", "schema.sql")
            dataload_path = os.path.join(base_dir, "sql", "dataload.sql")
            if os.path.exists(schema_path):
                with open(schema_path, encoding="utf-8") as f:
                    for stmt in f.read().split(";"):
                        s = stmt.strip()
                        if s:
                            await conn.execute(text(s))
            if os.path.exists(dataload_path):
                with open(dataload_path, encoding="utf-8") as f:
                    for stmt in f.read().split(";"):
                        s = stmt.strip()
                        if s:
                            await conn.execute(text(s))
