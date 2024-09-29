from models.base import Base
from models.mixin import IdMixin, TimestampMixin
from pydantic import EmailStr
from sqlalchemy import Column, String
from werkzeug.security import generate_password_hash


class User(IdMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)

    def __init__(
        self, email: EmailStr, password: str, username: str, full_name: str
    ) -> None:
        self.email = email
        self.username = username
        self.full_name = full_name
        self.hashed_password = generate_password_hash(password)

    def __repr__(self) -> str:
        return f"<User {self.email}>"
