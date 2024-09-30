from models.base import Base
from models.mixin import IdMixin, TimestampMixin
from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID


class Session(IdMixin, TimestampMixin, Base):
    __tablename__ = "sessions"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    access_jti = Column(UUID(as_uuid=True))
    refresh_jti = Column(UUID(as_uuid=True))
    session_exp = Column(DateTime)
