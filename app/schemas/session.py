from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field
from schemas.base import OrjsonBaseModel


class SessionResponse(OrjsonBaseModel):
    id: UUID = Field(..., title="Session ID")
    user_id: str = Field(..., title="User ID")
    login_time: datetime = Field(..., title="Login Time")
    logout_time: Optional[datetime] = Field(None, title="Logout Time")
    user_agent: Optional[str] = Field(None, title="User Agent")

    class Config:
        orm_mode = True
        from_attributes = True
