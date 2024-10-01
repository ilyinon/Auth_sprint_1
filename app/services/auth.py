from functools import lru_cache
from typing import Optional
from uuid import UUID

from async_fastapi_jwt_auth import AuthJWT
from core.config import auth_settings
from core.logger import logger
from db.pg import get_session
from db.redis import get_redis
from fastapi import Depends
from models.user import User
from redis.asyncio import Redis
from redis.asyncio.client import Pipeline
from schemas.auth import Credentials, TwoTokens
from services.cache import BaseCache
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class AuthService(BaseCache):
    def __init__(
        self, db: AsyncSession, redis: Redis, auth_jwt: AuthJWT, cache: BaseCache
    ):
        self.db = db
        self.redis = redis
        self._auth_jwt = auth_jwt
        # self._token_storage = token_storage

    async def store_token(self, token) -> None:
        async def _store_token_inner(pipeline: Pipeline):
            if token.access_token:
                await pipeline.setex(
                    name=token.access_token,
                    time=auth_settings.authjwt_access_expiration_in_seconds,
                    value=str(True),
                )
            if token.refresh_token:
                await pipeline.setex(
                    name=token.refresh_token,
                    time=auth_settings.authjwt_refresh_expiration_in_seconds,
                    value=str(True),
                )

        await self.redis.transaction(_store_token_inner)

    async def login(self, credentials: Credentials) -> Optional[TwoTokens]:
        result = await self.db.execute(
            select(User).where(User.email == credentials.username)
        )
        user = result.scalars().first()
        if not user or not user.check_password(credentials.password):
            logger.info(f"No creds: {credentials}")
            return None

        # self.redis.put_by_key
        tokens = await self.create_tokens(user)
        # await self._auth_jwt.set_access_cookies(tokens.access_token)
        # await self._auth_jwt.set_refresh_cookies(tokens.refresh_token)
        logger.info(f"let save tokens to cache: {tokens}")
        save_it = await self.store_token(tokens)
        await self._auth_jwt.set_access_cookies(tokens.access_token)
        await self._auth_jwt.set_refresh_cookies(tokens.refresh_token)
        logger.info(f"{save_it}")
        # session = Session(user_id = user.id)

        return tokens

    async def create_tokens(self, user: User) -> TwoTokens:
        access_token = await self._auth_jwt.create_access_token(
            subject=str(user.id), user_claims={"session_id": "session_id"}
        )
        refresh_token = await self._auth_jwt.create_refresh_token(
            subject=str(user.id), user_claims={"session_id": "session_id"}
        )
        refresh_jwt = await self._auth_jwt.get_raw_jwt(refresh_token)
        logger.info(f"my refresh_jwst: {refresh_jwt}")

        logger.info(f"my access_token: {access_token}")
        logger.info(f"my refresh_token: {refresh_token}")

        return TwoTokens(access_token=access_token, refresh_token=refresh_token)

    async def check_access(self) -> None:
        # from api.dependencies.get_user import GetUser, refresh_token_required
        #     if user.is_active:
        # raise HTTPException(
        #     status_code=status.HTTP_400_BAD_REQUEST,
        #     detail='The User had been already activated.'
        # )

        try:
            r = await self._auth_jwt.jwt_required()
        except Exception:
            return False

        logger.info(f"innter !!!! {r}")
        return True

    async def logout(self) -> None:
        access_jwt = await self.auth.jwt.get_raw_jwt()
        await self.end_session(access_jwt["session_id"])

    async def end_session(self, session_id: UUID):
        pass

    async def refresh_tokens(self, refresh_token: str) -> Optional[TwoTokens]:
        refresh_token = await self._auth_jwt.get_raw_jwt(refresh_token)


@lru_cache()
def get_auth_service(
    db: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    auth_jwt: AuthJWT = Depends(),
) -> AuthService:
    return AuthService(db, redis, auth_jwt, BaseCache)
