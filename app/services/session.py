from functools import lru_cache
import logging
import logging
from typing import Optional
from uuid import UUID

from fastapi import Depends
from db.redis import get_redis
from services.cache import BaseCache, RedisCacheEngine
from schemas.session import SessionResponse 
from redis.asyncio import Redis

logger = logging.getLogger(__name__)

class SessionService(BaseCache):
    def __init__(self, cache: BaseCache):
        super().__init__(cache)

    async def delete_session(self, session_id: UUID) -> None:
        await self.delete_by_key("session", session_id)

    async def store_session(self, session_id: UUID, session_data: SessionResponse, expiration: int) -> None:
        await self.put_by_key(session_data, expiration, "session", session_id)

    async def get_session(self, session_id: UUID) -> Optional[SessionResponse]:
        session_data = await self.get_by_key("session", session_id, SessionResponse)
        if session_data:
            return SessionResponse(**session_data)
        return None


@lru_cache()
def get_session_service(
    redis: Redis = Depends(get_redis)
) -> SessionService:
    redis_cache_engine = RedisCacheEngine(redis)
    cache_engine = BaseCache(redis_cache_engine)

    return SessionService(cache_engine)
