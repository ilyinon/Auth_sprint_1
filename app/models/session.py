from models.base import Base
from models.mixin import IdMixin, TimestampMixin
from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Session(IdMixin, TimestampMixin, Base):
    __tablename__ = "sessions"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user_agent = Column(Text, nullable=True)
    user_action = Column(String(100), nullable=False)  # login, logout, refresh

    user = relationship("User", back_populates="sessions", lazy="selectin")
