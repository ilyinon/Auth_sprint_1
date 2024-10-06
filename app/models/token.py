from datetime import datetime
from uuid import uuid4

from models.base import Base
from models.mixin import IdMixin
from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID


class Token(IdMixin, Base):
    __tablename__ = "tokens"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    access_token_jti = Column(UUID(as_uuid=True), default=uuid4)
    refresh_token_jti = Column(UUID(as_uuid=True), default=uuid4)

    exp = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now())
