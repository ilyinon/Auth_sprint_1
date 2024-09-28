from pydantic import EmailStr
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


from werkzeug.security import check_password_hash, generate_password_hash
from models.mixin import IdMixin, TimestampMixin
from models.base import Base


class User(IdMixin, TimestampMixin, Base):
    __tablename__ = 'users'

    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String)
    full_name = Column(String, nullable=False)

    def __init__(self, email: EmailStr, password: str, username: str, full_name: str) -> None:
        self.email = email
        self.username = username
        self.full_name = full_name
        self.hashed_password = generate_password_hash(password)

