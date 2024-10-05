import pytest
from redis.asyncio import Redis

from tests.functional.settings import test_settings


@pytest.fixture(scope="session")
async def redis_client():
    client = Redis.from_url(test_settings.redis_dsn)
    yield client
    await client.close()


@pytest.fixture(autouse=True)
async def redis_flushall(redis_client):
    """Truncate all data from Redis before each test."""
    await redis_client.flushall()
