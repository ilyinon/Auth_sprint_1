from typing import Union

from fastapi import APIRouter
from fastapi.security import HTTPBearer  # noqa: F401
from schemas.base import HTTPExceptionResponse, HTTPValidationError
from schemas.user import UserCreate, UserResponse

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    summary="User registration",
    responses={
        "400": {"model": HTTPExceptionResponse},
        "422": {"model": HTTPValidationError},
    },
    tags=["Registration"],
)
async def register(
    body: UserCreate,
) -> Union[UserResponse, HTTPExceptionResponse, HTTPValidationError]:
    """
    Registration
    """
    pass
