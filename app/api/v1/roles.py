from typing import List, Optional, Union
from uuid import UUID

from core.logger import logger
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from schemas.base import HTTPExceptionResponse, HTTPValidationError
from schemas.role import RoleBase, RoleResponse
from services.auth import AuthService, get_auth_service
from services.role import RoleService, get_role_service

get_token = HTTPBearer(auto_error=False)


router = APIRouter()

roles_with_allowed = [
    "admin",
]


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
async def list_roles(
    access_token: str = Depends(get_token),
    role_service: RoleService = Depends(get_role_service),
    auth_service: AuthService = Depends(get_auth_service),
) -> Union[List[RoleResponse], HTTPExceptionResponse]:

    if not access_token:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    logger.info(f"Check access for {access_token.credentials}")

    if not await auth_service.check_access_with_roles(
        access_token.credentials, roles_with_allowed
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    return await role_service.list_roles()


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
async def create_role(
    body: RoleBase,
    access_token: str = Depends(get_token),
    role_service: RoleService = Depends(get_role_service),
    auth_service: AuthService = Depends(get_auth_service),
) -> Union[RoleResponse, HTTPExceptionResponse, HTTPValidationError]:
    """
    Create role
    """
    if not access_token:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    if not await auth_service.check_access_with_roles(
        access_token.credentials, roles_with_allowed
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    new_role = await role_service.create_role(body)
    if new_role:
        return new_role


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
async def delete_role(
    role_id: UUID,
    access_token: str = Depends(get_token),
    role_service: RoleService = Depends(get_role_service),
    auth_service: AuthService = Depends(get_auth_service),
) -> Optional[Union[HTTPExceptionResponse, HTTPValidationError]]:
    """
    Delete role
    """
    if not access_token:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    logger.info(f"Check access for {access_token.credentials}")

    if not await auth_service.check_access_with_roles(
        access_token.credentials, roles_with_allowed
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    if await role_service.get_role_by_id(role_id):
        role_service.delete_role(role_id)
        return status.HTTP_200_OK


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
async def change_role(
    role_id: UUID,
    body: RoleBase,
    access_token: str = Depends(get_token),
    role_service: RoleService = Depends(get_role_service),
    auth_service: AuthService = Depends(get_auth_service),
) -> Union[RoleResponse, HTTPExceptionResponse, HTTPValidationError]:
    """
    Change role
    """
    if not access_token:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    logger.info(f"Check access for {access_token.credentials}")

    if not await auth_service.check_access_with_roles(
        access_token.credentials, roles_with_allowed
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    if not await role_service.get_role_by_id(role_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )
    updated_role = await role_service.update_role(role_id, body)
    if updated_role:
        return updated_role
