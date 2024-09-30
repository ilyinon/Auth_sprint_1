from db.pg import Base
from models.mixin import IdMixin, TimestampMixin


class Session(IdMixin, TimestampMixin, Base):
    __tablename__ = "sessions"

    pass
