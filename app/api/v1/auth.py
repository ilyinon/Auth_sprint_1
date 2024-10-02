from typing import Annotated, List, Optional, Union
from datetime import datetime, timedelta

from core.logger import logger
from fastapi import APIRouter, Body, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer  # noqa: F401
from schemas.auth import Credentials, TwoTokens
from schemas.base import HTTPExceptionResponse, HTTPValidationError
from schemas.role import AllowRole
from schemas.user import UserCreate, UserResponse, UserLoginModel
from services.auth import AuthService, get_auth_service
from services.user import UserService, get_user_service
from services.errors import UserAlreadyExists
from sqlmodel.ext.asyncio.session import AsyncSession
from db.pg import get_session

get_token = HTTPBearer(auto_error=False)
from db.redis import add_jti_to_blocklist
from services.utils import verify_password, create_access_token
from services.dependencies import AccessTokenBearer, RefreshTokenBearer

REFRESH_TOKEN_EXPIRY = 30

router = APIRouter()


@router.post(
    "/signup",
    response_model=UserResponse,
    summary="User registration",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": HTTPExceptionResponse},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": HTTPValidationError},
    },
    tags=["Registration"],
)
async def signup(
    user_create: UserCreate, user_service: UserService = Depends(get_user_service)
) -> Union[UserResponse, HTTPExceptionResponse, HTTPValidationError]:

    is_exist_email = await user_service.get_user_by_email(user_create.email)
    if is_exist_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The email is already in use",
        )
    is_exist_username = await user_service.get_user_by_username(user_create.username)
    if is_exist_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The usernmae is already in use",
        )
    logger.info(f"Request to create {user_create}")
    created_new_user = await user_service.create_user(user_create)
    return created_new_user


@router.post(
    "/login",
    response_model=TwoTokens,
    summary="User login",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionResponse},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": HTTPValidationError},
    },
    tags=["Authorization"],
)
async def login(
    login_data: UserLoginModel,
    auth_service: AuthService = Depends(get_auth_service),
    # session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
) -> Union[TwoTokens, HTTPExceptionResponse, HTTPValidationError]:

    email = login_data.email
    password = login_data.password
    user = await user_service.get_user_by_email(email)
    logger.info("point 1")
    logger.info(f"user is {user}")

    if user is not None:
        password_valid = verify_password(password, user.hashed_password)
        logger.info(f"password_valid is {password_valid}")

        if password_valid:
            user_data = {
                "email": user.email,
                "user_uid": str(user.id),
                "role": "admin",
            }
            access_token = await auth_service.create_access_token(user_data)

            user_data = {"email": user.email, "user_uid": str(user.id)}
            refresh_token = await auth_service.create_access_token(
                user_data, refresh=True, expiry=timedelta(days=REFRESH_TOKEN_EXPIRY)
            )
            tokens = TwoTokens(access_token=access_token, refresh_token=refresh_token)
            #   tokens = TwoTokens(access_token, refresh_token)
            logger.info(f"tokens to return is {tokens}")
            return tokens

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad username or password"
    )


@router.post(
    "/logout",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="User logout",
    responses={status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionResponse}},
    tags=["Authorization"],
)
async def logout(
    token_details: dict = Depends(AccessTokenBearer()),
) -> Optional[HTTPExceptionResponse]:
    jti = token_details["jti"]
    await add_jti_to_blocklist(jti)

    return status.HTTP_204_NO_CONTENT


@router.post(
    "/refresh",
    response_model=TwoTokens,
    summary="Refresh tokens",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionResponse},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": HTTPValidationError},
    },
    tags=["Authorization"],
)
async def refresh_tokens(
    token_details: dict = Depends(RefreshTokenBearer())
) -> Union[TwoTokens, HTTPExceptionResponse, HTTPValidationError]:
    expiry_timestamp = token_details["exp"]
    logger.info(f"token info {token_details}")
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(user_data=token_details["user"])
        logger.info(f"new tokens is {new_access_token}")
        return new_access_token

    raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )



@router.get(
    "/check_access",
    summary="Check access",
    response_model=None,
    responses={
        "401": {"model": HTTPExceptionResponse},
        "403": {"model": HTTPExceptionResponse},
        "422": {"model": HTTPValidationError},
    },
    tags=["Authorization"],
)
def check_access(
    allow_roles: Optional[List[AllowRole]] = None,
) -> Optional[Union[HTTPExceptionResponse, HTTPValidationError]]:
    """
    Check access
    """
    pass
