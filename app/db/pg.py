import os
from core.config import auth_settings
from sqlalchemy import create_engine


engine = create_engine(auth_settings.database_dsn, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session