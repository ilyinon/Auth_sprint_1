from redis.asyncio import Redis, from_url
from core.config import auth_settings


redis: Redis | None = None


async def get_redis() -> Redis:
    return redis


JTI_EXPIRY = 3600

token_blocklist = from_url(auth_settings.redis_dsn)


async def add_jti_to_blocklist(jti: str) -> None:
    await token_blocklist.set(name=jti, value="", ex=JTI_EXPIRY)


async def token_in_blocklist(jti: str) -> bool:
    jti = await token_blocklist.get(jti)

    return jti is not None
