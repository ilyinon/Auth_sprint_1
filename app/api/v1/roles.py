from typing import List, Optional, Union
from uuid import UUID

from core.logger import logger
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from schemas.auth import TokenPayload
from schemas.base import HTTPExceptionResponse, HTTPValidationError
from schemas.role import RoleBase, RoleResponse
from services.auth import AuthService, get_auth_service
from services.role import RoleService, get_role_service

get_token = HTTPBearer(auto_error=False)

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
async def list_roles(
    request: Request,
    access_token: str = Depends(get_token),
    role_service: RoleService = Depends(get_role_service),
    auth_service: AuthService = Depends(get_auth_service),
) -> Union[List[RoleResponse], HTTPExceptionResponse]:
    """
    List of roles
    """
    logger.info(f"get roles with token {access_token.credentials}")

    if access_token:
        logger.info(f"Check access for {access_token.credentials}")

        if await auth_service.check_access_with_roles(
            access_token.credentials, ["user"]
        ):

            return await role_service.list_roles()

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    # except Exception as e:
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail="Could not retrieve roles",
    # )


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
    body: RoleBase, role_service: RoleService = Depends(get_role_service)
) -> Union[RoleResponse, HTTPExceptionResponse, HTTPValidationError]:
    """
    Create role
    """
    # try:
    return await role_service.create_role(body)
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create role"
    #     )


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
    role_id: UUID, role_service: RoleService = Depends(get_role_service)
) -> Optional[Union[HTTPExceptionResponse, HTTPValidationError]]:
    """
    Delete role
    """
    # try:
    role = await role_service.get_role_by_id(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )
    await role_service.delete_role(role_id)
    return None
    # except HTTPException as e:
    #     raise e
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail="Failed to delete role",
    #     )


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
    role_id: UUID, body: RoleBase, role_service: RoleService = Depends(get_role_service)
) -> Union[RoleResponse, HTTPExceptionResponse, HTTPValidationError]:
    """
    Change role
    """
    # try:
    role = await role_service.get_role_by_id(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )
    updated_role = await role_service.update_role(role_id, body)
    return updated_role
    # except HTTPException as e:
    #     raise e
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail="Failed to update role",
    #     )
