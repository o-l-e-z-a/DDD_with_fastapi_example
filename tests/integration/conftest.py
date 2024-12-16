import asyncio

import httpx
import pytest

from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.config import AsyncSessionFactory, engine
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

    yield engine

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
    transport = httpx.ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
async def async_session(
) -> AsyncSession:
    async with AsyncSessionFactory() as session:
        yield session
        await session.rollback()
    async with engine.begin() as conn:
        for table in Base.metadata.sorted_tables:
            await conn.execute(text(f"TRUNCATE TABLE public.{table.name} CASCADE"))


@pytest.fixture()
def user_repo(async_session) -> UserRepository:
    return UserRepository(session=async_session)


@pytest.fixture()
def user_point_repo(async_session) -> UserPointRepository:
    return UserPointRepository(session=async_session)


async def add_to_tb(repo, entity):
    entity.id = None
    added_entity = await repo.add(entity)
    await repo.session.commit()
    entity.id = added_entity.id
    added_entity_with_joins = await repo.find_one_or_none(id=added_entity.id)
    return added_entity_with_joins


@pytest.fixture()
async def user_ivanov_db(user_repo, user_ivanov):
    user = await add_to_tb(user_repo, user_ivanov)
    return user


@pytest.fixture()
async def user_petrov_db(user_repo, user_petrov):
    user = await add_to_tb(user_repo, user_petrov)
    return user


@pytest.fixture()
async def ivanov_user_point_db(user_point_repo, ivanov_user_point):
    user_point = await add_to_tb(user_point_repo, ivanov_user_point)
    return user_point


@pytest.fixture()
async def petrov_user_point_db(user_point_repo, petrov_user_point):
    user_point = await add_to_tb(user_point_repo, petrov_user_point)
    return user_point


@pytest.fixture()
def user_service_db(
) -> UserService:
    uow = SQLAlchemyUsersUnitOfWork(
    )
    return UserService(uow)


@pytest.fixture()
def user_service_with_db_data(
    user_service_db, user_ivanov_db, ivanov_user_point_db, user_petrov_db, petrov_user_point_db
) -> UserService:
    return user_service_db
