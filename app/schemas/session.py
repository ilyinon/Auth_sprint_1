from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field
from schemas.base import OrjsonBaseModel


class SessionResponse(OrjsonBaseModel):
    id: UUID = Field(..., title="Session ID")
    user_id: str = Field(..., title="User ID")
    user_agent: Optional[str] = Field(None, title="User Agent")
    user_action: str = Field(..., title="User Action")
    created_at: datetime = Field(..., title="Created At")

    class Config:
        orm_mode = True
        from_attributes = True
