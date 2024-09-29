from functools import lru_cache
from typing import Optional

from async_fastapi_jwt_auth import AuthJWT
from core.logger import logger
from db.pg import get_session
from db.redis import get_redis
from fastapi import Depends
from models.user import User
from redis.asyncio import Redis
from schemas.auth import Credentials, TwoTokens
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class AuthService:
    def __init__(self, db: AsyncSession, redis: Redis, auth_jwt: AuthJWT):
        self.db = db
        self.redis = redis
        self.auth_jwt = auth_jwt

    async def login(self, credentials: Credentials) -> Optional[TwoTokens]:
        result = await self.db.execute(
            select(User).where(User.email == credentials.username)
        )
        user = result.scalars().first()
        if not user or not user.check_password(credentials.password):
            logger.info(f"No creds: {credentials}")
            return None

        return await self.create_tokens(user)

    async def create_tokens(self, user: User) -> TwoTokens:
        access_token = await self.auth_jwt.create_access_token(
            subject=str(user.id), user_claims={"session_id": "session_id"}
        )
        refresh_token = await self.auth_jwt.create_refresh_token(
            subject=str(user.id), user_claims={"session_id": "session_id"}
        )
        refresh_jwt = await self.auth_jwt.get_raw_jwt(refresh_token)
        logger.info(f"my refresh_jwst: {refresh_jwt}")

        logger.info(f"my access_token: {access_token}")
        logger.info(f"my refresh_token: {refresh_token}")

        return TwoTokens(access_token=access_token, refresh_token=refresh_token)

    async def logout():
        pass

    async def refresh_tokens():
        pass

    async def check_access():
        pass


@lru_cache()
def get_auth_service(
    db: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    auth_jwt: AuthJWT = Depends(),
) -> AuthService:
    return AuthService(db, redis, auth_jwt)
