import asyncio

import pytest

from httpx import AsyncClient
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.infrastructure.db.config import engine
from src.infrastructure.db.models.base import Base
from src.infrastructure.db.repositories.users import UserPointRepository, UserRepository
from src.logic.uows.users_uow import SQLAlchemyUsersUnitOfWork
from src.presentation.api.main import app as fastapi_app
from src.presentation.api.settings import settings
from tests.unit.domain.conftest import *
from tests.unit.logic.conftest import *


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    assert settings.MODE == "TEST"

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def ac():
    async with AsyncClient(app=fastapi_app, base_url="http://test") as ac:
        yield ac


@pytest.fixture()
async def async_session() -> AsyncSession:
    # async with AsyncSessionFactory() as session:
    #     yield session

    connection = await engine.connect()
    trans = await connection.begin()

    session_maker = async_sessionmaker(
        connection,
        expire_on_commit=False,
    )
    async with session_maker() as session:
        yield session



    # try:
    #     yield session
    # finally:
    #     await session.close()
    #     await trans.rollback()
    #     await connection.close()


@pytest.fixture()
def user_repo(async_session) -> UserRepository:
    return UserRepository(session=async_session)


@pytest.fixture()
def user_point_repo(async_session) -> UserPointRepository:
    return UserPointRepository(session=async_session)


@pytest.fixture()
async def user_ivanov_db(user_repo, user_ivanov):
    user = await user_repo.add(user_ivanov)
    # await user_repo.session.commit()
    return user


@pytest.fixture()
async def user_point_db(user_point_repo, ivanov_user_point):
    user_point = await user_point_repo.add(ivanov_user_point)
    # await user_point_repo.session.commit()
    return user_point


@pytest.fixture()
def user_service_db() -> UserService:
    uow = SQLAlchemyUsersUnitOfWork()
    return UserService(uow)


@pytest.fixture()
def user_service_with_db_data(user_service_db, user_ivanov_db, user_point_db) -> UserService:
    return user_service_db
