from typing import List, Optional, Union
from uuid import UUID

from fastapi import APIRouter
from fastapi.security import HTTPBearer  # noqa: F401
from schemas.base import HTTPExceptionResponse, HTTPValidationError
from schemas.role import RoleBase, RoleResponse

router = APIRouter()


@router.get(
    "/",
    response_model=List[RoleResponse],
    summary="List all available roles",
    responses={
        "401": {"model": HTTPExceptionResponse},
        "403": {"model": HTTPExceptionResponse},
    },
    tags=["Manage roles"],
)
def list_roles() -> Union[List[RoleResponse], HTTPExceptionResponse]:
    """
    List of roles
    """
    pass


@router.post(
    "/",
    response_model=RoleResponse,
    summary="Create new role",
    responses={
        "400": {"model": HTTPExceptionResponse},
        "401": {"model": HTTPExceptionResponse},
        "403": {"model": HTTPExceptionResponse},
        "422": {"model": HTTPValidationError},
    },
    tags=["Manage roles"],
)
def create_role(
    body: RoleBase,
) -> Union[RoleResponse, HTTPExceptionResponse, HTTPValidationError]:
    """
    Create role
    """
    pass


@router.delete(
    "/{role_id}",
    response_model=None,
    summary="Delete exist role",
    responses={
        "401": {"model": HTTPExceptionResponse},
        "403": {"model": HTTPExceptionResponse},
        "404": {"model": HTTPExceptionResponse},
        "422": {"model": HTTPValidationError},
    },
    tags=["Manage roles"],
)
def delete_role(
    role_id: UUID,
) -> Optional[Union[HTTPExceptionResponse, HTTPValidationError]]:
    """
    Delete role
    """
    pass


@router.patch(
    "/{role_id}",
    response_model=RoleResponse,
    summary="Update one of exist role",
    responses={
        "401": {"model": HTTPExceptionResponse},
        "403": {"model": HTTPExceptionResponse},
        "404": {"model": HTTPExceptionResponse},
        "422": {"model": HTTPValidationError},
    },
    tags=["Manage roles"],
)
def change_role(
    role_id: UUID, body: RoleBase = ...
) -> Union[RoleResponse, HTTPExceptionResponse, HTTPValidationError]:
    """
    Change role
    """
    pass
