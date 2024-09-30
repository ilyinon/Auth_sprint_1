from models.base import Base
from models.mixin import IdMixin, TimestampMixin
from sqlalchemy import Column, String


class Role(IdMixin, TimestampMixin, Base):
    __tablename__ = "roles"

    name = Column(String, unique=True, nullable=False)
