from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field
from schemas.base import OrjsonBaseModel


class SessionResponse(OrjsonBaseModel):
    id: UUID = Field(..., title="Id")
    user_agent: str = Field(..., title="User Agent")
    created_at: datetime = Field(..., title="Created At")
    action: str = Field(..., title="action")

    class Config:
        orm_mode = True
        from_attributes = True
