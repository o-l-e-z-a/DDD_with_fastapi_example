import asyncio
import datetime

from pydantic import PositiveInt

from src.infrastructure.db.config import AsyncSessionFactory
from src.infrastructure.db.repositories.users import UserRepository
from src.logic.dto.order_dto import OrderCreateDTO, TotalAmountDTO
from src.logic.dto.schedule_dto import InventoryAddDTO, InventoryUpdateDTO, MasterAddDTO, ScheduleAddDTO
from src.logic.dto.user_dto import UserCreateDTO
from src.logic.services.order_service import OrderService
from src.logic.services.schedule_service import MasterService, ProcedureService, ScheduleService
from src.logic.services.users_service import UserService
from src.logic.uows.order_uow import SQLAlchemyOrderUnitOfWork
from src.logic.uows.schedule_uow import SQLAlchemyScheduleUnitOfWork
from src.logic.uows.users_uow import SQLAlchemyUsersUnitOfWork


async def add_user():
    uow = SQLAlchemyUsersUnitOfWork()
    u_s = UserService(uow)
    dto = UserCreateDTO(
        email="master@masterov.ru",
        first_name="master",
        last_name="masterov",
        telephone="88005553537",
        password="Admin@14",
    )
    user = await u_s.add_user(dto)
    user_id = user.id
    # user_id = 11

    user = await u_s.get_user_by_id(user_id)
    print(user)
    user_point = await u_s.get_user_point(user)
    print(user_point)


async def add_inventory():
    uow = SQLAlchemyScheduleUnitOfWork()
    u_s = ProcedureService(uow)
    dto = InventoryAddDTO(name="лак", unit="мл", stock_count=PositiveInt(1000))
    inventory = await u_s.add_inventory(dto)
    print(inventory)

    inventory_update_dto = InventoryUpdateDTO(name="Лак")
    inventory_after_update = await u_s.update_inventory(inventory_update_dto, inventory.id)
    print(inventory_after_update)

    print(await u_s.get_inventories())


async def get_services():
    uow = SQLAlchemyScheduleUnitOfWork()
    u_s = ProcedureService(uow)
    print(await u_s.get_services())


async def add_master():
    uow = SQLAlchemyScheduleUnitOfWork()
    u_s = MasterService(uow)
    dto = MasterAddDTO(description="мастер по окрашиванию", user_id=11, services_id=[1])
    inventory = await u_s.add_master(dto)
    print(inventory)
    print(await u_s.get_all_masters())
    print(await u_s.get_all_user_to_add_masters())
    print(await u_s.get_masters_for_service(1))


async def add_schedule():
    uow = SQLAlchemyScheduleUnitOfWork()
    u_s = ScheduleService(uow)
    service_id = 1
    master_id = 4
    day = datetime.date(year=2024, month=12, day=25)
    dto = ScheduleAddDTO(
        day=day,
        service_id=service_id,
        master_id=master_id,
    )
    # inventory = await u_s.add_schedule(dto)
    # print(inventory)

    print(await u_s.get_schedules())
    print(await u_s.get_slot_for_day(3))
    print(
        await u_s.get_day_for_master(
            service_id=service_id,
            master_id=master_id,
        )
    )
    print(await u_s.get_master_days(master_id=master_id))
    print(await u_s.get_current_master_slots(day=day, master_id=master_id))


async def add_order():
    uow = SQLAlchemyOrderUnitOfWork()
    u_s = OrderService(uow)
    async with AsyncSessionFactory() as session:
        repo = UserRepository(session)
        new_user_id = 11
        user = await repo.find_one_or_none(id=new_user_id)
    print(user)
    total_amount_dto = TotalAmountDTO(
        schedule_id=3,
        point="0",
    )
    dto = OrderCreateDTO(
        total_amount=total_amount_dto,
        time_start="11:00",
    )
    total_amount = await u_s.get_total_amount(total_amount_dto=total_amount_dto, user=user)
    print(total_amount)

    # order = await u_s.add_order(dto, user)
    # print(order)

    print(await u_s.get_all_orders())
    print(await u_s.get_client_orders(user))


if __name__ == "__main__":
    # asyncio.get_event_loop().run_until_complete(add_user())
    # asyncio.get_event_loop().run_until_complete(add_inventory())
    # asyncio.get_event_loop().run_until_complete(get_services())
    # asyncio.get_event_loop().run_until_complete(add_schedule())
    asyncio.get_event_loop().run_until_complete(add_order())
