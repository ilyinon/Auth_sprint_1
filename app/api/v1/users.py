from typing import List, Optional, Union
from uuid import UUID

from fastapi import APIRouter
from fastapi.security import HTTPBearer  # noqa: F401
from pydantic import conint
from schemas.auth import Credentials, RefreshToken, TwoTokens  # noqa: F401
from schemas.base import HTTPExceptionResponse, HTTPValidationError
from schemas.role import RoleBaseUUID
from schemas.session import SessionResponse
from schemas.user import UserPatch, UserResponse

router = APIRouter()


@router.delete(
    "/sessions/{session_id}",
    response_model=None,
    summary="Delete user session",
    responses={
        "401": {"model": HTTPExceptionResponse},
        "404": {"model": HTTPExceptionResponse},
        "422": {"model": HTTPValidationError},
    },
    tags=["Manage sessions"],
)
def delete_user_session(
    session_id: UUID,
) -> Optional[Union[HTTPExceptionResponse, HTTPValidationError]]:
    """
    Delete session
    """
    pass


@router.get(
    "/sessions",
    response_model=List[SessionResponse],
    summary="History of user activities",
    responses={
        "401": {"model": HTTPExceptionResponse},
        "422": {"model": HTTPValidationError},
    },
    tags=["Manage sessions"],
)
def get_user_sessions(
    active: Optional[bool] = None,
    page_size: Optional[conint(ge=1)] = 50,
    page_number: Optional[conint(ge=1)] = 1,
) -> Union[List[SessionResponse], HTTPExceptionResponse, HTTPValidationError]:
    """
    History of user activities
    """
    pass


@router.post(
    "/{user_id}/roles",
    response_model=None,
    summary="Add role to user",
    responses={
        "400": {"model": HTTPExceptionResponse},
        "401": {"model": HTTPExceptionResponse},
        "403": {"model": HTTPExceptionResponse},
        "422": {"model": HTTPValidationError},
    },
    tags=["Manage access"],
)
def add_role_to_user(
    user_id: UUID, body: RoleBaseUUID = ...
) -> Optional[Union[HTTPExceptionResponse, HTTPValidationError]]:
    """
    Add user role
    """
    pass


@router.delete(
    "/{user_id}/roles",
    summary="Take away role from user",
    response_model=None,
    responses={
        "401": {"model": HTTPExceptionResponse},
        "403": {"model": HTTPExceptionResponse},
        "404": {"model": HTTPExceptionResponse},
        "422": {"model": HTTPValidationError},
    },
    tags=["Manage access"],
)
def take_away_role_from_user(
    user_id: UUID, body: RoleBaseUUID = ...
) -> Optional[Union[HTTPExceptionResponse, HTTPValidationError]]:
    """
    Delete user role
    """
    pass


@router.get(
    "/",
    response_model=UserResponse,
    summary="Get user details",
    responses={
        "401": {"model": HTTPExceptionResponse},
        "404": {"model": HTTPExceptionResponse},
    },
    tags=["User profile"],
)
def get_user_info() -> Union[UserResponse, HTTPExceptionResponse]:
    """
    Get user profile
    """
    pass


@router.patch(
    "/",
    response_model=UserResponse,
    responses={
        "401": {"model": HTTPExceptionResponse},
        "404": {"model": HTTPExceptionResponse},
        "422": {"model": HTTPValidationError},
    },
    tags=["User profile"],
)
def patch_current_user(
    body: UserPatch,
) -> Union[UserResponse, HTTPExceptionResponse, HTTPValidationError]:
    """
    Change user profile
    """
    pass
