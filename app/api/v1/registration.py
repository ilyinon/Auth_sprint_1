import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from schemas.base import HTTPExceptionResponse, HTTPValidationError

from schemas.user import UserCreate, UserResponse
from typing import List, Optional, Union
from db.pg import get_session, init_db

router = APIRouter()


@router.post(
    '/register',
    response_model=UserResponse,
    summary='User registration',
    responses={
        '400': {'model': HTTPExceptionResponse},
        '422': {'model': HTTPValidationError},
    },
    tags=['Registration'],
)
async def register(
    body: UserCreate,
) -> Union[UserResponse, HTTPExceptionResponse, HTTPValidationError]:
    """
    Registration
    """
    pass