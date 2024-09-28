from typing import List, Optional, Union

from fastapi import APIRouter
from fastapi.security import HTTPBearer  # noqa: F401
from schemas.auth import Credentials, RefreshToken, TokenPair
from schemas.base import HTTPExceptionResponse, HTTPValidationError
from schemas.role import AllowRole
from schemas.user import UserCreate, UserResponse

router = APIRouter()


@router.post(
    "/signup",
    response_model=UserResponse,
    summary="User registration",
    responses={
        "400": {"model": HTTPExceptionResponse},
        "422": {"model": HTTPValidationError},
    },
    tags=["Registration"],
)
async def signup(
    body: UserCreate,
) -> Union[UserResponse, HTTPExceptionResponse, HTTPValidationError]:
    """
    Registration
    """
    pass


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
