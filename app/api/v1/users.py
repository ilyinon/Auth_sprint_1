from typing import List, Optional, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import conint
from schemas.auth import RefreshToken, TwoTokens
from schemas.base import HTTPExceptionResponse, HTTPValidationError
from schemas.role import RoleBaseUUID
from schemas.session import SessionResponse
from schemas.user import UserPatch, UserResponse
from services.auth import AuthService, get_auth_service
from services.session import SessionService, get_session_service
from services.user import UserService, get_user_service

router = APIRouter()


@router.delete(
    "/sessions/{session_id}",
    summary="Delete user session",
    responses={
        "401": {"model": HTTPExceptionResponse},
        "404": {"model": HTTPExceptionResponse},
        "422": {"model": HTTPValidationError},
    },
    tags=["Manage sessions"],
)
async def delete_user_session(
    session_id: UUID,
    session_service: SessionService = Depends(get_session_service),
    auth_service: AuthService = Depends(get_auth_service),
) -> Optional[Union[HTTPExceptionResponse, HTTPValidationError]]:
    """
    Delete user session by session ID.
    """
    await auth_service.check_access()  # Ensure the user is authenticated

    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    await session_service.delete_session(session_id)
    return {"message": "Session deleted successfully."}


PageSizeType = Optional[conint(ge=1)]


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
async def get_user_sessions(
    active: Optional[bool] = None,
    page_size: PageSizeType = 50,
    page_number: PageSizeType = 1,
    session_service: SessionService = Depends(get_session_service),
    auth_service: AuthService = Depends(get_auth_service),
) -> Union[List[SessionResponse], HTTPExceptionResponse]:
    """
    Retrieve user's session history with optional pagination and activity filter.
    """
    await auth_service.check_access()  # Ensure the user is authenticated

    # Simulate session retrieval from cache or database using the service
    sessions = await session_service.get_all_sessions()  # Implement in service
    if not sessions:
        return []

    # Optional pagination logic
    start = (page_number - 1) * page_size
    end = start + page_size

    return sessions[start:end]


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
async def add_role_to_user(
    user_id: UUID,
    body: RoleBaseUUID,
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
) -> Optional[Union[HTTPExceptionResponse, HTTPValidationError]]:
    """
    Add a role to a user.
    """
    await auth_service.check_access()  # Ensure the user is authenticated

    try:
        await user_service.add_role_to_user(user_id, body)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return None


@router.delete(
    "/{user_id}/roles",
    summary="Remove role from user",
    response_model=None,
    responses={
        "401": {"model": HTTPExceptionResponse},
        "403": {"model": HTTPExceptionResponse},
        "404": {"model": HTTPExceptionResponse},
        "422": {"model": HTTPValidationError},
    },
    tags=["Manage access"],
)
async def take_away_role_from_user(
    user_id: UUID,
    body: RoleBaseUUID,
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
) -> Optional[Union[HTTPExceptionResponse, HTTPValidationError]]:
    """
    Remove a role from a user.
    """
    await auth_service.check_access()  # Ensure the user is authenticated

    try:
        await user_service.remove_role_from_user(user_id, body)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return None


@router.get(
    "/",
    response_model=UserResponse,
    summary="Get user details",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionResponse},
        status.HTTP_404_NOT_FOUND: {"model": HTTPExceptionResponse},
    },
    tags=["User profile"],
)
async def get_user_info(
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
) -> Union[UserResponse, HTTPExceptionResponse]:
    """
    Retrieve current user's information.
    """
    await auth_service.check_access()  # Ensure the user is authenticated

    user = await user_service.get_current_user()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


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
async def patch_current_user(
    body: UserPatch,
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
) -> Union[UserResponse, HTTPExceptionResponse, HTTPValidationError]:
    """
    Update the current user's profile.
    """
    await auth_service.check_access()  # Ensure the user is authenticated

    try:
        updated_user = await user_service.update_user(body)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return updated_user
