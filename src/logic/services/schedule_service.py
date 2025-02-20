from datetime import date
from typing import Sequence

from sqlalchemy import RowMapping

from src.domain.schedules.entities import Master, Order, Schedule, Service, Slot, SlotsForSchedule
from src.domain.schedules.values import SlotTime
from src.domain.users.entities import User
from src.infrastructure.db.uows.order_uow import SQLAlchemyOrderUnitOfWork
from src.infrastructure.db.uows.schedule_uow import SQLAlchemyScheduleUnitOfWork
from src.logic.exceptions.schedule_exceptions import ScheduleNotFoundLogicException


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
