import logging
from functools import lru_cache
from typing import Optional
from uuid import UUID

import jwt as jwt_auth
from models.role import Role
from schemas.role import RoleBaseUUID
from schemas.session import SessionResponse
from db.pg import get_session
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from models.user import User
from pydantic import EmailStr
from schemas.user import UserCreate, UserPatch, UserResponse, UserResponseLogin
from services.database import BaseDb, PostgresqlEngine
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, db: BaseDb, auth_jwt: jwt_auth):
        self.db = db
        self.auth_jwt = auth_jwt

    async def get_user_by_email(self, email: EmailStr) -> Optional[UserResponse]:
        logger.info(f"Checking if user with email {email} exists")
        user = await self.db.get_by_key("email", email, User)
        if user:
            return UserResponseLogin.from_orm(user)
        return None

    async def get_user_by_username(self, username: str) -> Optional[UserResponse]:
        logger.info(f"Checking if user with username {username} exists")
        user = await self.db.get_by_key("username", username, User)
        if user:
            return UserResponse.from_orm(user)
        return None

    async def create_user(self, user_create: UserCreate) -> UserResponse:
        user = User(**user_create.dict())
        logger.info(f"Creating a new user with data: {user_create}")
        new_user = await self.db.create(user, User)
        return UserResponse.from_orm(new_user)

    async def get_current_user(self, user_id: UUID) -> Optional[UserResponse]:
        user = await self.db.get_by_id(user_id, User)
        if user:
            return UserResponse.from_orm(user)
        return None

    async def update_user(self, user_id: UUID, user_patch: UserPatch) -> Optional[UserResponse]:
        current_user = await self.db.get_by_id(user_id, User)

        if not current_user:
            return "User not found"

        user_data = jsonable_encoder(user_patch, exclude_unset=True)

        updated_user = await self.db.update(user_id, user_data)
        if updated_user:
            return UserResponse.from_orm(updated_user)

    async def delete_user(self, user_id: UUID) -> None:
        await self.db.delete(user_id, User)

    async def add_role_to_user(self, user_id: UUID, role_data: RoleBaseUUID) -> None:
        user = await self.db.get_by_id(user_id, User)
        if not user:
            raise ValueError("User not found")

        role = await self.db.get_by_id(role_data.role_id, Role)
        if not role:
            raise ValueError("Role not found")

        user.roles.append(role)
        await self.db.update(user_id, user)

    async def remove_role_from_user(self, user_id: UUID, role_data: RoleBaseUUID) -> None:
        user = await self.db.get_by_id(user_id, User)
        if not user:
            raise ValueError("User not found")

        role = await self.db.get_by_id(role_data.role_id, Role)
        if not role:
            raise ValueError("Role not found")

        user.roles.remove(role)
        await self.db.update(user_id, user)

@lru_cache()
def get_user_service(
    db_session: AsyncSession = Depends(get_session)
) -> UserService:

    db_engine = PostgresqlEngine(db_session)
    base_db = BaseDb(db_engine)
    return UserService(base_db, jwt_auth)
