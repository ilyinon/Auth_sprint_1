from collections.abc import AsyncIterator
from uuid import UUID, uuid4

import pytest
from pytest_alembic import MigrationContext
from pytest_postgresql.janitor import DatabaseJanitor
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
    select,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import text
from tests.models.role import Role, UserRole
from tests.models.session import Session
from tests.models.token import Token
from tests.models.user import User

from tests.functional.settings import test_settings

from sqlalchemy.ext.asyncio import create_async_engine  # isort: skip


engine = create_engine(test_settings.database_dsn_not_async)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


@pytest.fixture()
def _run_migrations(alembic_runner: MigrationContext):
    alembic_runner.migrate_up_to("heads", return_current=False)


@pytest.fixture(scope="session")
def db() -> Session:

    with SessionLocal() as db_session:
        yield db_session


pg = test_settings.database_dsn_not_async


@pytest.fixture()
def alembic_engine():
    return create_engine(pg)


@pytest.fixture
def admin_role(db: Session, _run_migrations) -> dict:
    user = User(
        email="admin@example.com",
        password="admin_user",
        username="Adm None",
        full_name="secret",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
    # return db_session.execute(select(Role))


@pytest.fixture(scope="module")
def create_test_data():
    users = [
        ["admin@example.com", "admin_user", "Adm None", "secret"],
        ["user@example.com", "user_user", "User None", "not_secret"],
    ]
    return [
        User(email=email, username=username, full_name=full_name, password=password)
        for email, username, full_name, password in users
    ]


# @pytest.fixture()
# def async_engine(pg_container: ) -> AsyncEngine:
#     return create_async_engine(
#         pg_container.get_connection_url(),
#         poolclass=NullPool,
#     )


# @pytest.fixture()
# def alembic_engine( pg_container: PostgresContainer) -> AsyncEngine:
#     return create_async_engine(
#         pg_container.get_connection_url(),
#         poolclass=NullPool,
#     )

# @pytest.fixture()
# def _run_migrations(alembic_runner: MigrationContext):
#     alembic_runner.migrate_up_to("heads", return_current=False)


# @pytest.fixture()
# async def session(async_engine, _run_migrations) -> AsyncIterator[AsyncSession]:
#     async with AsyncSession(
#         async_engine, expire_on_commit=False, autoflush=False, autocommit=False
#     ) as session:
#         yield session
