from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from models.base import Base
from models.mixin import IdMixin, TimestampMixin


class Session(IdMixin, TimestampMixin, Base):
    __tablename__ = "sessions"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    login_time = Column(DateTime, nullable=False)
    logout_time = Column(DateTime, nullable=True)
    user_agent = Column(String, nullable=True)

    user = relationship("User", back_populates="sessions", lazy="selectin")
