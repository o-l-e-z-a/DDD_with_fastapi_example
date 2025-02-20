from datetime import date
from typing import Sequence

from sqlalchemy import RowMapping

from src.domain.schedules.entities import Master, Order, Schedule, Service, Slot, SlotsForSchedule
from src.domain.schedules.values import SlotTime
from src.domain.users.entities import User
from src.infrastructure.db.uows.order_uow import SQLAlchemyOrderUnitOfWork
from src.infrastructure.db.uows.schedule_uow import SQLAlchemyScheduleUnitOfWork
from src.logic.exceptions.schedule_exceptions import ScheduleNotFoundLogicException


class ProcedureService:
    def __init__(self, uow: SQLAlchemyScheduleUnitOfWork):
        self.uow = uow

    async def get_services(self) -> list[Service]:
        async with self.uow:
            services = await self.uow.services.find_all()
        return services


class MasterService:
    def __init__(self, uow: SQLAlchemyScheduleUnitOfWork):
        self.uow = uow

    async def get_master_by_user(self, user: User) -> Master | None:
        async with self.uow:
            master = await self.uow.masters.find_one_or_none(user_id=user.id)
        return master

    async def get_all_masters(self) -> list[Master]:
        async with self.uow:
            masters = await self.uow.masters.find_all()
        return masters

    async def get_all_user_to_add_masters(self) -> list[User]:
        async with self.uow:
            masters = await self.uow.masters.get_users_to_masters()
        return masters

    async def get_masters_for_service(self, service_id: int) -> list[Master]:
        async with self.uow:
            masters = await self.uow.masters.filter_by_service(service_id=service_id)
        return masters

    async def get_master_report(self) -> dict[str, int | str]:
        async with self.uow:
            masters = await self.uow.masters.get_order_report_by_master()
        return masters


class ScheduleService:
    def __init__(self, uow: SQLAlchemyScheduleUnitOfWork):
        self.uow = uow

    async def get_schedules(self) -> list[Schedule]:
        async with self.uow:
            schedules = await self.uow.schedules.find_all()
        return schedules

    async def get_master_days(self, master_id: int) -> list[date]:
        async with self.uow:
            days = await self.uow.schedules.get_schedule_for_master(master_id=master_id)
        return days

    async def get_day_for_master(self, master_id: int, service_id: int) -> list[date]:
        async with self.uow:
            days = await self.uow.schedules.get_schedule_for_master(master_id=master_id, service_id=service_id)
        return days

    async def get_slot_for_schedule(self, schedule_id: int) -> list[SlotTime]:
        async with self.uow:
            schedule = await self.uow.schedules.find_one_or_none(id=schedule_id)
            if not schedule:
                raise ScheduleNotFoundLogicException(id=schedule_id)
            occupied_slots = await self.uow.slots.find_all(day=schedule.day)
        free_slots = SlotsForSchedule().get_free_slots(occupied_slots=occupied_slots)
        return free_slots

    async def get_current_master_slots(self, day: date, master_id: int) -> list[Slot]:
        async with self.uow:
            slots = await self.uow.slots.find_all(day=day, master_id=master_id)
        return slots


class OrderService:
    def __init__(self, uow: SQLAlchemyOrderUnitOfWork):
        self.uow = uow

    async def get_all_orders(self) -> list[Order]:
        async with self.uow:
            orders = await self.uow.orders.find_all()
        return orders

    async def get_client_orders(self, user: User) -> list[Order]:
        async with self.uow:
            orders = await self.uow.orders.find_all(user_id=user.id)
        return orders

    async def get_service_report(self) -> Sequence[RowMapping]:
        async with self.uow:
            orders = await self.uow.orders.get_order_report_by_service()
        return orders
