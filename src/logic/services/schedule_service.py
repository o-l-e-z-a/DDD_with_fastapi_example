from datetime import date
from typing import Sequence, Type

from src.domain.base.values import BaseValueObject, CountNumber, Name
from src.domain.schedules.entities import Inventory, Master, Schedule, Service, Slot, SlotsForSchedule
from src.domain.schedules.values import SlotTime
from src.domain.users.entities import User
from src.logic.dto.schedule_dto import InventoryAddDTO, InventoryUpdateDTO, MasterAddDTO, ScheduleAddDTO
from src.logic.exceptions.schedule_exceptions import InventoryNotFoundLogicException, ServiceNotFoundLogicException, \
    MasterNotFoundLogicException, ScheduleNotFoundLogicException
from src.logic.exceptions.user_exceptions import UserNotFoundLogicException
from src.logic.uows.schedule_uow import SQLAlchemyScheduleUnitOfWork


class ProcedureService:
    def __init__(self, uow: SQLAlchemyScheduleUnitOfWork):
        self.uow = uow

    async def get_services(self) -> Sequence[Service]:
        async with self.uow:
            services = await self.uow.services.find_all()
        return services

    async def get_inventories(self) -> Sequence[Inventory]:
        async with self.uow:
            inventories = await self.uow.inventories.find_all()
        return inventories

    async def add_inventory(self, inventory_data: InventoryAddDTO) -> Inventory:
        async with self.uow:
            inventory = Inventory(
                name=Name(inventory_data.name),
                stock_count=CountNumber(inventory_data.stock_count),
                unit=Name(inventory_data.unit),
            )
            inventory_from_repo = await self.uow.inventories.add(entity=inventory)
            await self.uow.commit()
            return inventory_from_repo

    async def update_inventory(self, inventory_data: InventoryUpdateDTO) -> Inventory:
        async with self.uow:
            inventory = await self.uow.inventories.find_one_or_none(id=inventory_data.inventory_id)
            if not inventory:
                raise InventoryNotFoundLogicException(inventory_data.inventory_id)
            key_mapper: dict[str, Type[BaseValueObject]] = {
                "name": Name,
                "unit": Name,
                "stock_count": CountNumber,
            }
            for k, v in inventory_data.model_dump(exclude_none=True, exclude={'inventory_id'}).items():
                setattr(inventory, k, key_mapper.get(k)(value=v))
            inventory_from_repo = await self.uow.inventories.update(entity=inventory)
            await self.uow.commit()
            return inventory_from_repo

    async def delete_inventory(self, inventory_id: int):
        async with self.uow:
            await self.uow.inventories.delete(id=inventory_id)
            await self.uow.commit()


class MasterService:
    def __init__(self, uow: SQLAlchemyScheduleUnitOfWork):
        self.uow = uow

    async def get_master_by_user(self, user: User) -> Master | None:
        async with self.uow:
            master = await self.uow.masters.find_one_or_none(user_id=user.id)
        return master

    async def get_all_masters(self) -> Sequence[Master]:
        async with self.uow:
            masters = await self.uow.masters.find_all()
        return masters

    async def get_all_user_to_add_masters(self) -> Sequence[User]:
        async with self.uow:
            masters = await self.uow.masters.get_users_to_masters()
        return masters

    async def add_master(self, master_data: MasterAddDTO) -> Master:
        async with self.uow:
            services = await self.uow.services.get_services_by_ids(master_data.services_id)
            if not services:
                raise ServiceNotFoundLogicException(id=master_data.services_id)
            user = await self.uow.users.find_one_or_none(id=master_data.user_id)
            if not user:
                raise UserNotFoundLogicException(id=master_data.user_id)
            master = Master(
                description=master_data.description,
                user=user,
                services=services,
            )
            master_from_repo = await self.uow.masters.add(entity=master)
            await self.uow.commit()
            return await self.uow.masters.find_one_or_none(id=master_from_repo.id)

    async def get_masters_for_service(self, service_int: int) -> list[Master]:
        async with self.uow:
            masters = await self.uow.masters.filter_by_service(service_id=service_int)
        return masters

    async def get_master_report(self):
        pass


class ScheduleService:
    def __init__(self, uow: SQLAlchemyScheduleUnitOfWork):
        self.uow = uow

    async def get_schedules(self) -> list[Schedule]:
        async with self.uow:
            schedules = await self.uow.schedules.find_all()
        return schedules

    async def add_schedule(self, schedule_data: ScheduleAddDTO) -> Schedule:
        async with self.uow:
            service = await self.uow.services.find_one_or_none(id=schedule_data.service_id)
            if not service:
                raise ServiceNotFoundLogicException(id=schedule_data.services_id)
            master = await self.uow.masters.find_one_or_none(id=schedule_data.master_id)
            if not master:
                raise MasterNotFoundLogicException(id=schedule_data.master_id)
            schedule = Schedule(day=schedule_data.day, service=service, master=master)
            schedule_from_repo = await self.uow.schedules.add(entity=schedule)
            await self.uow.commit()
            return await self.uow.schedules.find_one_or_none(id=schedule_from_repo.id)

    async def get_master_days(self, master_id: int) -> list[date]:
        async with self.uow:
            days = await self.uow.schedules.get_day_for_master(master_id=master_id)
        return days

    async def get_day_for_master(self, master_id: int, service_id: int) -> list[date]:
        async with self.uow:
            days = await self.uow.schedules.get_day_for_master(master_id=master_id, service_id=service_id)
        return days

    async def get_slot_for_day(self, schedule_id: int) -> list[SlotTime]:
        async with self.uow:
            schedule = await self.uow.schedules.find_one_or_none(id=schedule_id)
            if not schedule:
                raise ScheduleNotFoundLogicException(id=schedule_id)
            occupied_slots = await self.uow.slots.find_all(day=schedule.day)
        free_slots = SlotsForSchedule().get_free_slots(occupied_slots=occupied_slots)
        return free_slots

    async def get_current_master_slots(self, day: date, master_id: int) -> list[Slot]:
        async with self.uow:
            # slots = await self.uow.slots.find_all(schedule_day=day, master_id=master_id)
            slots = await self.uow.slots.find_all(day=day, master_id=master_id)
        return slots
