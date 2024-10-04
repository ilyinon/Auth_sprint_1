from typing import Annotated, List, Literal, Optional, Union

from core.logger import logger
from fastapi import APIRouter, Body, Depends, Query, Request, Response, status
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer  # noqa: F401
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from schemas.auth import Credentials, TwoTokens, UserLoginModel
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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


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

    is_exist_user = await user_service.get_user_by_email(user_create.email)
    if is_exist_user:
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
    form_data: UserLoginModel,
    request: Request,
    response: Response,
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
) -> Union[TwoTokens, HTTPExceptionResponse, HTTPValidationError]:
    if await user_service.get_user_by_email(form_data.email):
        logger.info(f"user agent is {request.headers.get('user-agent')}")
        tokens = await auth_service.login(form_data.email, form_data.password)
        if tokens:
            return tokens
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad username or password"
    )


@router.post(
    "/logout",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="User logout",
    responses={status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionResponse}},
    tags=["Authorization"],
)
async def logout(
    request: Request,
    access_token: str = Depends(get_token),
    auth_service: AuthService = Depends(get_auth_service),
) -> Optional[HTTPExceptionResponse]:
    user_agent = request.headers.get("user-agent")
    logger.info(f"Log out for {access_token.credentials}")

    if await auth_service.check_access(creds=access_token.credentials):
        await auth_service.logout(access_token.credentials)
        return status.HTTP_200_OK

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


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
async def check_access(
    request: Request,
    access_token: str = Depends(get_token),
    allow_roles: Literal["admin", "user"] = None,
    auth_service: AuthService = Depends(get_auth_service),
) -> Optional[Union[HTTPExceptionResponse, HTTPValidationError]]:
    logger.info(f"Check access for {access_token.credentials}")

    if await auth_service.check_access_with_roles(
        creds=access_token.credentials, allow_roles=allow_roles
    ):
        return status.HTTP_200_OK

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
