from core.config import auth_settings
from sqlalchemy import create_engine
from sqlalchemy.ext import Session

engine = create_engine(auth_settings.database_dsn, echo=True)


def get_session():
    with Session(engine) as session:
        yield session
