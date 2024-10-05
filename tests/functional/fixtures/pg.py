import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import text

from tests.functional.settings import test_settings

from sqlalchemy.ext.asyncio import create_async_engine  # isort: skip
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker  # isort: skip

Base = declarative_base()

engine = create_async_engine(test_settings.database_dsn, echo=True, future=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
async def db() -> AsyncSession:
    async with async_session() as pg_session:
        yield pg_session


@pytest.fixture(autouse=True)
async def db_truncate(db: AsyncSession):
    """Truncate data in PG before each test."""
    for table in ["users", "roles", "user_roles"]:
        await db.execute(text(f"TRUNCATE {table} CASCADE"))
    await db.commit()
