from typing import List, Optional, Union

from core.logger import logger
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer  # noqa: F401
from schemas.auth import Credentials, RefreshToken, TokenPair
from schemas.base import HTTPExceptionResponse, HTTPValidationError
from schemas.role import AllowRole
from schemas.user import UserCreate, UserResponse
from services.user import UserService, get_user_service

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
    logger.info(f"wanna create {user_create}")
    created_new_user = await user_service.create_user(user_create)
    return created_new_user


@router.post(
    "/login",
    response_model=TokenPair,
    summary="User login",
    responses={
        "401": {"model": HTTPExceptionResponse},
        "422": {"model": HTTPValidationError},
    },
    tags=["Authorization"],
)
def login(
    body: Credentials,
) -> Union[TokenPair, HTTPExceptionResponse, HTTPValidationError]:
    """
    Log in
    """
    pass


@router.post(
    "/logout",
    response_model=None,
    summary="User logout",
    responses={"401": {"model": HTTPExceptionResponse}},
    tags=["Authorization"],
)
def logout() -> Optional[HTTPExceptionResponse]:
    """
    Log out
    """
    pass


@router.post(
    "/refresh",
    response_model=TokenPair,
    summary="Refresh tokens",
    responses={
        "401": {"model": HTTPExceptionResponse},
        "422": {"model": HTTPValidationError},
    },
    tags=["Authorization"],
)
def refresh_tokens(
    body: RefreshToken,
) -> Union[TokenPair, HTTPExceptionResponse, HTTPValidationError]:
    """
    Refresh token
    """
    pass


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
