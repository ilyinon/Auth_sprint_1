import logging
from functools import lru_cache
from typing import Optional

from async_fastapi_jwt_auth import AuthJWT
from db.pg import get_session
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from models.user import User
from pydantic import EmailStr
from schemas.user import UserCreate, UserResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, db: AsyncSession, auth_jwt: AuthJWT):
        self.db = db
        self.auth_jwt = auth_jwt

    async def get_user_by_email(self, email: EmailStr) -> Optional[UserResponse]:
        logger.info(f"Check if user with {email} exist")
        result = await self.db.execute(select(User).where(User.email == email))
        logger.info(f"Got the response {result}")
        return result.scalars().first()

    async def create_user(self, user_create: UserCreate) -> UserResponse:
        user = User(**jsonable_encoder(user_create))
        logger.info("Going to create a new user {user_create}")
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_current_user(self) -> Optional[UserResponse]:
        user_id = await self.auth_jwt.get_jwt_subject()
        get_user = await self.db.execute(select(User).where(User.id == user_id))
        return get_user


@lru_cache()
def get_user_service(
    db: AsyncSession = Depends(get_session), auth_jwt: AuthJWT = Depends()
) -> UserService:
    return UserService(db, auth_jwt)
