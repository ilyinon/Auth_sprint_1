from uuid import UUID

from pydantic import EmailStr, Field
from schemas.base import OrjsonBaseModel


class UserBase(OrjsonBaseModel):
    email: EmailStr
    username: str = Field(title="Username")
    full_name: str = Field(title="Full Name")


class UserCreate(UserBase):
    password: str = Field(title="Password")


class UserResponse(UserBase):
    id: UUID

    class Config:
        orm_mode = True
