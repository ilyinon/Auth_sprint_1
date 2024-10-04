import json

from async_fastapi_jwt_auth import AuthJWT
from db.pg import get_session
from db.redis import get_redis
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from models.user import User
from redis.asyncio import Redis
from schemas.user import UserResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(HTTPBearer()),
    redis: Redis = Depends(get_redis),
    db: AsyncSession = Depends(get_session),
    Authorize: AuthJWT = Depends(),
) -> UserResponse:

    token = credentials.credentials

    try:
        await Authorize._verifying_token(token)
    except Exception:
        return None

    data = await Authorize.get_raw_jwt(token)
    if token and data["type"] != "access":
        return None

    user_tokens = json.loads(await redis.get(data.get("sub")))
    if token not in user_tokens.values():
        return None

    r = await db.execute(select(User).where(User.email == data.get("email")))
    user = r.scalar()
    if not user:
        None

    return UserResponse(
        id=data.get("sub"),
        email=data.get("email"),
        # role_id=data.get('role_id')
    )
