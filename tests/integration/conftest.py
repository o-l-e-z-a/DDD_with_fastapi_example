import asyncio

from functools import wraps
from unittest import mock

import httpx
import pytest
import pytest_asyncio

from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.config import AsyncSessionFactory, engine
from src.infrastructure.db.models.base import Base
from src.infrastructure.db.repositories.orders import PromotionRepository, UserPointRepository
from src.infrastructure.db.repositories.schedules import (
    # ConsumablesRepository,
    # InventoryRepository,
    MasterRepository,
    ScheduleRepository,
    ServiceRepository,
    SlotRepository,
    OrderRepository
)
from src.infrastructure.db.repositories.users import UserRepository
from src.logic.services.order_service import PromotionService
from src.logic.services.schedule_service import MasterService, ProcedureService
from src.logic.services.users_service import get_password_hash
from src.logic.uows.order_uow import SQLAlchemyOrderUnitOfWork
from src.logic.uows.schedule_uow import SQLAlchemyScheduleUnitOfWork
from src.logic.uows.users_uow import SQLAlchemyUsersUnitOfWork
from src.presentation.api.orders.schema import OrderCreateSchema
from src.presentation.api.schedules.schema import SlotCreateSchema
from src.presentation.api.settings import settings
from tests.unit.domain.conftest import *
from tests.unit.logic.conftest import *


def mock_cache(*args, **kwargs):
    def wrapper(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            return await func(*args, **kwargs)

        return inner

    return wrapper


mock.patch("fastapi_cache.decorator.cache", mock_cache).start()


@pytest_asyncio.fixture(loop_scope="session", scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(loop_scope="session", scope="session", autouse=True)
async def prepare_database():
    assert settings.MODE == "TEST"

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture()
async def ac():
    from src.presentation.api.main import app as fastapi_app
    transport = httpx.ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture()
async def ac_with_login_ivanov(ac, user_service_db_data, user_ivanov_dto):
    await ac.post("/auth/login/", json=user_ivanov_dto.model_dump())
    yield ac


@pytest.fixture()
async def ac_with_master_login(ac, schedule_service_db_data, master_login_dto):
    await ac.post("/auth/login/", json=master_login_dto.model_dump())
    yield ac


@pytest.fixture()
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


# @pytest.fixture()
# def consumables_repo(async_session) -> ConsumablesRepository:
#     return ConsumablesRepository(session=async_session)
#
#
# @pytest.fixture()
# def inventory_repo(async_session) -> InventoryRepository:
#     return InventoryRepository(session=async_session)


@pytest.fixture()
def master_repo(async_session) -> MasterRepository:
    return MasterRepository(session=async_session)


@pytest.fixture()
def schedule_repo(async_session) -> ScheduleRepository:
    return ScheduleRepository(session=async_session)


@pytest.fixture()
def service_repo(async_session) -> ServiceRepository:
    return ServiceRepository(session=async_session)


@pytest.fixture()
def slot_repo(async_session) -> SlotRepository:
    return SlotRepository(session=async_session)


@pytest.fixture()
def promotion_repo(async_session) -> PromotionRepository:
    return PromotionRepository(session=async_session)


@pytest.fixture()
def order_repo(async_session) -> OrderRepository:
    return OrderRepository(session=async_session)


async def add_to_tb(repo, entity):
    entity.id = None
    added_entity = await repo.add(entity)
    await repo.session.commit()
    entity.id = added_entity.id
    added_entity_with_joins = await repo.find_one_or_none(id=added_entity.id)
    return added_entity_with_joins


@pytest.fixture()
async def user_ivanov_db(user_repo, user_ivanov):
    user_ivanov.hashed_password = get_password_hash(PASSWORD)
    user = await add_to_tb(user_repo, user_ivanov)
    return user


@pytest.fixture()
async def user_petrov_db(user_repo, user_petrov):
    user_petrov.hashed_password = get_password_hash(PASSWORD)
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


# @pytest.fixture()
# async def henna_inventory_db(inventory_repo, henna_inventory):
#     inventory = await add_to_tb(inventory_repo, henna_inventory)
#     return inventory
#
#
# @pytest.fixture()
# async def shampoo_inventory_db(inventory_repo, shampoo_inventory):
#     inventory = await add_to_tb(inventory_repo, shampoo_inventory)
#     return inventory


# @pytest.fixture()
# async def henna_consumable_db(consumables_repo, henna_consumable):
#     consumable = await add_to_tb(consumables_repo, henna_consumable)
#     return consumable
#
#
# @pytest.fixture()
# async def shampoo_consumable_db(consumables_repo, shampoo_consumable):
#     consumable = await add_to_tb(consumables_repo, shampoo_consumable)
#     return consumable
#
#
@pytest.fixture()
async def henna_staining_service_db(service_repo, henna_staining_service):
    service = await add_to_tb(service_repo, henna_staining_service)
    return service


@pytest.fixture()
async def shampooing_service_db(service_repo, shampooing_service):
    service = await add_to_tb(service_repo, shampooing_service)
    return service


@pytest.fixture()
async def henna_and_shampooing_master_db(master_repo, henna_and_shampooing_master):
    master = await add_to_tb(master_repo, henna_and_shampooing_master)
    return master


@pytest.fixture()
async def henna_staining_today_schedule_db(schedule_repo, henna_staining_today_schedule):
    schedule = await add_to_tb(schedule_repo, henna_staining_today_schedule)
    return schedule


@pytest.fixture()
async def shampooing_tomorrow_schedule_db(schedule_repo, shampooing_tomorrow_schedule):
    schedule = await add_to_tb(schedule_repo, shampooing_tomorrow_schedule)
    return schedule


@pytest.fixture()
async def henna_staining_today_12_slot_db(slot_repo, henna_staining_today_12_slot):
    slot = await add_to_tb(slot_repo, henna_staining_today_12_slot)
    return slot


@pytest.fixture()
async def henna_staining_today_14_slot_db(slot_repo, henna_staining_today_14_slot):
    slot = await add_to_tb(slot_repo, henna_staining_today_14_slot)
    return slot


@pytest.fixture()
async def henna_staining_today_12_order_db(order_repo, henna_staining_today_12_order):
    order = await add_to_tb(order_repo, henna_staining_today_12_order)
    return order


@pytest.fixture()
async def promotion_20_db(promotion_repo, promotion_20):
    promotion = await add_to_tb(promotion_repo, promotion_20)
    return promotion


@pytest.fixture()
async def henna_staining_today_14_order_db(order_repo, henna_staining_today_14_order):
    order = await add_to_tb(order_repo, henna_staining_today_14_order)
    return order


@pytest.fixture()
def user_service_db() -> UserService:
    uow = SQLAlchemyUsersUnitOfWork()
    return UserService(uow)


@pytest.fixture()
def schedule_service_db() -> ScheduleService:
    uow = SQLAlchemyScheduleUnitOfWork()
    return ScheduleService(uow)


@pytest.fixture()
def master_service_db() -> MasterService:
    uow = SQLAlchemyScheduleUnitOfWork()
    return MasterService(uow)


@pytest.fixture()
def procedure_service_db() -> ProcedureService:
    uow = SQLAlchemyScheduleUnitOfWork()
    return ProcedureService(uow)


@pytest.fixture()
def promotion_service_db() -> PromotionService:
    uow = SQLAlchemyOrderUnitOfWork()
    return PromotionService(uow)


@pytest.fixture()
def order_service_db() -> OrderService:
    uow = SQLAlchemyOrderUnitOfWork()
    return OrderService(uow)


@pytest.fixture()
def db_users(user_ivanov_db, ivanov_user_point_db, user_petrov_db, petrov_user_point_db):
    return user_ivanov_db, ivanov_user_point_db, user_petrov_db, petrov_user_point_db


@pytest.fixture()
def inventories_db(henna_inventory_db, shampoo_inventory_db, henna_consumable_db, shampoo_consumable_db):
    return henna_inventory_db, shampoo_inventory_db, henna_consumable_db, shampoo_consumable_db


@pytest.fixture()
def procedures_db(henna_staining_service_db, shampooing_service_db, henna_and_shampooing_master_db):
    return henna_staining_service_db, shampooing_service_db, henna_and_shampooing_master_db


@pytest.fixture()
def schedule_db(
    henna_staining_today_schedule_db, shampooing_tomorrow_schedule_db,
    henna_staining_today_12_slot_db, henna_staining_today_14_slot_db,
):
    return henna_staining_today_schedule_db, shampooing_tomorrow_schedule_db, \
        henna_staining_today_12_slot_db, henna_staining_today_14_slot_db,


@pytest.fixture()
def order_db(henna_staining_today_12_order_db, henna_staining_today_14_order_db, promotion_20_db):
    return henna_staining_today_12_order_db, henna_staining_today_14_order_db, promotion_20_db


@pytest.fixture()
def user_service_db_data(user_service_db, db_users) -> UserService:
    return user_service_db


@pytest.fixture()
def procedure_service_db_data(procedure_service_db, db_users, inventories_db, procedures_db) -> ProcedureService:
    return procedure_service_db


@pytest.fixture()
def master_service_db_data(master_service_db, db_users, inventories_db, procedures_db) -> MasterService:
    return master_service_db


@pytest.fixture()
def schedule_service_db_data(
    schedule_service_db, db_users, inventories_db, procedures_db, schedule_db
) -> ScheduleService:
    return schedule_service_db


@pytest.fixture()
def promotion_service_db_data(
    promotion_service_db, db_users, inventories_db, procedures_db, schedule_db, order_db
) -> PromotionService:
    return promotion_service_db


@pytest.fixture()
def order_service_db_data(
    order_service_db, db_users, inventories_db, procedures_db, schedule_db, order_db
) -> OrderService:
    return order_service_db


@pytest.fixture()
def old_access_token():
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMyIsImV4cCI6MTczMzk3MTUxMiwidHlwZSI6ImFjY2VzcyJ9." \
           "Nwxzu8J0yrlqMeVPuSY1jD461P0geFanBoKwssnBAfc"


@pytest.fixture()
def invalid_access_token():
    return "adasdasasdasdasdasd.eyJzdWIiOiIxMyIsImV4cCI6MTczMzk3MTUxMiwidHlwZSI6ImFjY2VzcyJ9." \
           "Nwxzu8J0yrlqMeVPuSY1jD461P0geFanBoKwssnBAfc"


@pytest.fixture()
def new_schedule_model_added_dict(shampooing_service, henna_and_shampooing_master):
    return {
        'day': '2024-07-08',
        'master': {
            'description': henna_and_shampooing_master.description,
            'id': henna_and_shampooing_master.id,
            'user': {
                'date_birthday': None,
                'email': henna_and_shampooing_master.user.email.as_generic_type(),
                'first_name': henna_and_shampooing_master.user.first_name.as_generic_type(),
                'id': henna_and_shampooing_master.user.id,
                'is_admin': False,
                'last_name': henna_and_shampooing_master.user.last_name.as_generic_type(),
                'telephone': henna_and_shampooing_master.user.telephone.as_generic_type()
            }
        },
        'service': {
            'description': shampooing_service.description,
            'id': shampooing_service.id,
            'name': shampooing_service.name.as_generic_type(),
            'price': shampooing_service.price.as_generic_type()
        }
    }


@pytest.fixture()
def new_order_added_dict(new_order_model):
    return {
        'photo_after_path': None,
        'photo_before_path': None,
        'point_uses': new_order_model.point_uses.as_generic_type(),
        'promotion_sale': new_order_model.promotion_sale.as_generic_type(),
        'slot': {
            'id': new_order_model.slot.id,
            'schedule': {'day': str(new_order_model.slot.schedule.day)},
            'time_start': new_order_model.slot.time_start.as_generic_type()
        },
        'total_amount': new_order_model.total_amount.as_generic_type(),
    }


@pytest.fixture()
def new_order_add_schema(new_order_dto):
    return OrderCreateSchema(
        point=new_order_dto.total_amount.point,
        promotion_code=new_order_dto.total_amount.promotion_code,
        slot=SlotCreateSchema(
            time_start=new_order_dto.time_start,
            schedule_id=new_order_dto.total_amount.schedule_id
        )
    )
