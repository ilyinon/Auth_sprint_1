from typing import Annotated, List, Optional, Union

from core.logger import logger
from fastapi import APIRouter, Body, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer  # noqa: F401
from schemas.auth import Credentials, TwoTokens
from schemas.base import HTTPExceptionResponse, HTTPValidationError
from schemas.role import AllowRole
from schemas.user import UserCreate, UserResponse
from services.auth import AuthService, get_auth_service
from services.user import UserService, get_user_service

get_token = HTTPBearer(auto_error=False)


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
    credentials: Credentials, auth_service: AuthService = Depends(get_auth_service)
) -> Union[TwoTokens, HTTPExceptionResponse, HTTPValidationError]:
    tokens = await auth_service.login(credentials)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad username or password"
        )
    return tokens


@router.post(
    "/logout",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="User logout",
    responses={status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionResponse}},
    tags=["Authorization"],
)
async def logout(
    access_token: str = Depends(get_token),
    auth_service: AuthService = Depends(get_auth_service),
) -> Optional[HTTPExceptionResponse]:
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad username or password"
        )
    await auth_service.check_access()
    await auth_service.logout()


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
    refresh_token: Annotated[str, Body(embed=True)],
    auth_service: AuthService = Depends(get_auth_service),
) -> Union[TwoTokens, HTTPExceptionResponse, HTTPValidationError]:
    refreshed_tokens = await auth_service.refresh_tokens(refresh_token)
    if not refreshed_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No token to refresh"
        )
    return refreshed_tokens


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
