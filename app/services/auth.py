from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Optional
from uuid import UUID, uuid4

import jwt as jwt_auth
from core.config import auth_settings
from core.logger import logger
from db.pg import get_session
from db.redis import add_jti_to_blocklist, get_redis
from fastapi import Depends
from models.role import Role, UserRole
from models.user import User

# from services.user imporst User
from pydantic import EmailStr
from redis.asyncio import Redis
from schemas.auth import Credentials, Payload, TwoTokens
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


class AuthService:
    def __init__(self, db: AsyncSession, redis: Redis):
        self.db = db
        self.redis = redis
        self.auth_jwt = jwt_auth

    async def login(self, email, hashed_password) -> Optional[TwoTokens]:
        logger.info("Start to login procedure")
        result = await self.get_user_by_email(email)
        user = result.scalars().first()
        logger.info(f"User has the following entry in db {user}")
        if user:
            if user.check_password(hashed_password):
                logger.info(f"User {email} provided the correct password")
                user_roles = await self.db.execute(
                    select(Role.name).where(UserRole.user_id == user.id).join(UserRole)
                )
                logger.info(f"User {email} has roles {user_roles}")
                user_data = {
                    "email": user.email,
                    "user_id": str(user.id),
                    "roles": [role for role in user_roles],
                }
                return await self.create_tokens(user, True, user_data)

        logger.info(f"Failed to login {email}")
        return None

    async def get_user_by_email(self, email: EmailStr) -> Optional[User]:
        logger.info(f"Get user by email {email}")
        return await self.db.execute(select(User).where(User.email == email))

    async def create_tokens(
        self, user: User, is_exist: bool = True, user_data={}
    ) -> TwoTokens:

        access_token = await self.create_token(user, user_data, False)
        logger.info(f"access token is {access_token}")

        refresh_token = await self.create_token(user, user_data, True)
        logger.info(f"refresh token is {refresh_token}")
        return TwoTokens(access_token=access_token, refresh_token=refresh_token)

    async def create_token(
        self,
        user: User,
        user_data={},
        refresh=False,
    ):
        logger.info("Start to create token")
        logger.info(f"User data is user_data")
        expires_time = datetime.now(tz=timezone.utc) + timedelta(
            seconds=auth_settings.jwt_access_token_expires_in_seconds
        )
        logger.info(f"expires_time is {expires_time}")

        payload = {}

        payload["user"] = user_data

        payload["exp"] = expires_time
        payload["jti"] = str(uuid4())

        payload["refresh"] = refresh

        token = jwt_auth.encode(
            payload=payload,
            key=auth_settings.authjwt_secret_key,
            algorithm=auth_settings.authjwt_algorithm,
        )
        logger.info("Token is generated")
        return token

    async def check_access(self, creds) -> None:
        logger.info(f"Check access for token {creds}")
        try:
            result = (await self.verify_jwt(creds)).user
            logger.info(f"The result is {result}")

        except Exception as e:
            logger.info(e)
            return None
        return result

    async def check_access_with_roles(
        self, creds, allow_roles: list[str] = None
    ) -> None:
        user_payload = await self.check_access(creds)
        if user_payload:
            logger.info("check roles if allow")
            if user_payload.get("roles", None):
                logger.info("User has no roles")

            else:
                if allow_roles:
                    logger.info(f"check if user has permission is {allow_roles}")
                    if not set(allow_roles) & set(user_payload.get("roles", "fake")):
                        return None
                return user_payload
        return False

    async def verify_jwt(self, jwtoken: str) -> bool:
        logger.info("Start to verify")
        try:
            logger.info("Start to get payload from decode_jwt")
            payload = await self.decode_jwt(jwtoken)
            logger.info(f"Get payload from decode_jwt {payload}")
        except:
            return None
        logger.info(f"Payload is {payload}")
        return Payload(**payload)

    async def decode_jwt(self, token: str) -> dict:
        logger.info("Start to decode")
        try:
            decoded_token = self.auth_jwt.decode(
                token,
                key=auth_settings.authjwt_secret_key,
                algorithms=auth_settings.authjwt_algorithm,
            )
            logger.info(f"decoded token is {decoded_token}")
            return decoded_token
        except Exception as e:
            logger.error(e)
            return False

    async def logout(self, access_token: str) -> None:
        logger.info(f"Logout user {access_token}")
        decoded_token = await self.decode_jwt(access_token)
        if not decoded_token:
            return False
        logger.info(f"decoded token for logout is {decoded_token}")

        await self.end_session(decoded_token["jti"])

    async def end_session(self, jti):
        logger.info(f"End session for {jti}")

        await self.revoke_access_token(jti)

    async def revoke_access_token(self, jti: UUID):
        await add_jti_to_blocklist(jti)

    async def refresh_tokens(self, refresh_token: str) -> Optional[TwoTokens]:
        logger.info("From auth service start to refresh token")
        decoded_token = await self.decode_jwt(refresh_token)
        logger.info(f"decoded refresh token: {decoded_token}")
        user = await self.get_user_by_email(decoded_token["user"]["email"])
        logger.info(f"get user to refresh: {user}")
        if user:
            if decoded_token["refresh"]:
                return await self.create_tokens(user, True, decoded_token["user"])
        return False

    async def is_token_in_redis(self, refresh_token: str) -> bool:
        decoded_token = await self.decode_jwt(refresh_token)
        if decoded_token and await self.redis.exists(decoded_token["jti"]):
            return True
        return False


@lru_cache()
def get_auth_service(
    db: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
) -> AuthService:
    return AuthService(db, redis)
