from dataclasses import dataclass
from datetime import date
from tempfile import SpooledTemporaryFile
from typing import Annotated, BinaryIO

from pydantic import BaseModel, Field, PositiveInt

from src.domain.schedules.entities import Master, Order, Schedule
from src.infrastructure.db.uows.schedule_uow import SQLAlchemyScheduleUnitOfWork
from src.infrastructure.logger_adapter.logger import init_logger
from src.logic.commands.base import BaseCommand, CommandHandler
from src.logic.events.schedule_events import OrderCreatedEvent
from src.logic.exceptions.order_exceptions import NotUserOrderLogicException
from src.logic.exceptions.schedule_exceptions import (
    MasterNotFoundLogicException,
    OrderNotFoundLogicException,
    ServiceNotFoundLogicException,
    SlotNotFoundLogicException,
)
from src.logic.exceptions.user_exceptions import UserNotFoundLogicException

logger = init_logger(__name__)


class AddMasterCommand(BaseCommand):
    description: str
    user_id: PositiveInt
    services_id: list[PositiveInt]


@dataclass(frozen=True)
class AddMasterCommandHandler(CommandHandler[AddMasterCommand, Master]):
    uow: SQLAlchemyScheduleUnitOfWork

    async def handle(self, command: AddMasterCommand) -> Master:
        async with self.uow:
            services = await self.uow.services.get_services_by_ids(command.services_id)
            if not services:
                raise ServiceNotFoundLogicException(id=command.services_id)
            user = await self.uow.users.find_one_or_none(id=command.user_id)
            if not user:
                raise UserNotFoundLogicException(id=command.user_id)
            master = Master(
                description=command.description,
                user_id=command.user_id,
                services_id=command.services_id,
            )
            master_from_repo = await self.uow.masters.add(entity=master)
            await self.uow.commit()
        return master_from_repo


class AddScheduleCommand(BaseCommand):
    day: date
    master_id: PositiveInt


@dataclass(frozen=True)
class AddScheduleCommandHandler(CommandHandler[AddScheduleCommand, Schedule]):
    uow: SQLAlchemyScheduleUnitOfWork

    async def handle(self, command: AddScheduleCommand) -> Schedule:
        async with self.uow:
            master = await self.uow.masters.find_one_or_none(id=command.master_id)
            if not master:
                raise MasterNotFoundLogicException(id=command.master_id)
            schedule = Schedule.add(day=command.day, master_id=command.master_id)
            schedule_from_repo = await self.uow.schedules.add(entity=schedule)
            await self.uow.commit()
        return schedule_from_repo


slot_type = Annotated[str, Field(pattern=r"^(?:[01][0-9]|2?[0-3]):[0-5]\d$")]


class AddOrderCommand(BaseCommand):
    slot_id: PositiveInt
    service_id: PositiveInt
    user_id: PositiveInt


@dataclass(frozen=True)
class AddOrderCommandHandler(CommandHandler[AddOrderCommand, Order]):
    uow: SQLAlchemyScheduleUnitOfWork

    async def handle(self, command: AddOrderCommand) -> Order:
        async with self.uow:
            logger.debug(f"{self.__class__.__name__}: async with uow: {self.uow}, {self.uow._session}")
            service = await self.uow.services.find_one_or_none(id=command.service_id)
            if not service:
                raise ServiceNotFoundLogicException(id=command.service_id)
            slot = await self.uow.schedules.find_one_or_none_slot(slot_id=command.slot_id)
            if not slot:
                raise SlotNotFoundLogicException(id=command.slot_id)
            schedule_master_services_ids = await self.uow.schedules.find_master_services_by_schedule(
                schedule_id=slot.schedule_id
            )
            occupied_slots = await self.uow.schedules.find_occupied_slots(schedule_id=slot.schedule_id)
            occupied_slots_ids = [slot.id for slot in occupied_slots]
            order_from_aggregate = Order.add(
                user_id=command.user_id,
                service_id=command.service_id,
                slot_id=command.slot_id,
                schedule_master_services_ids=schedule_master_services_ids,
                occupied_slots_ids=occupied_slots_ids,
            )
            order_from_repo = await self.uow.orders.add(order_from_aggregate)
            logger.debug(f"{self.__class__.__name__}: uow.commit()")
            events = order_from_aggregate.pull_events()
            created_event = OrderCreatedEvent(
                order_id=order_from_repo.id,
                slot_time_start=slot.time_start.as_generic_type(),
                schedule_id=slot.schedule_id,
                user_id=order_from_repo.user_id,
                service_name=service.name.as_generic_type(),
                service_price=service.price.as_generic_type(),
            )
            events.append(created_event)
            logger.debug(f"{self.__class__.__name__}: created_event, {created_event}")
            await self.uow.outbox.bulk_add(events)
            logger.debug(f"{self.__class__.__name__}: после медиатор паблиш")
            await self.uow.commit()
        return order_from_repo


class UpdateOrderCommand(BaseCommand):
    order_id: PositiveInt
    slot_id: PositiveInt
    user_id: PositiveInt


@dataclass(frozen=True)
class UpdateOrderCommandHandler(CommandHandler[UpdateOrderCommand, Order]):
    uow: SQLAlchemyScheduleUnitOfWork

    async def handle(self, command: UpdateOrderCommand) -> Order:
        async with self.uow:
            order = await self.uow.orders.find_one_or_none(id=command.order_id)
            if not order:
                raise OrderNotFoundLogicException(id=command.order_id)
            elif not order.user_id == command.user_id:
                raise NotUserOrderLogicException()
            slot = await self.uow.schedules.find_one_or_none_slot(slot_id=command.slot_id)
            if not slot:
                raise SlotNotFoundLogicException(id=command.slot_id)
            occupied_slots = await self.uow.schedules.find_occupied_slots(schedule_id=slot.schedule_id)
            order.update_slot_time(slot_id=command.slot_id, occupied_slots=occupied_slots)
            await self.uow.orders.update(order)
            events = order.pull_events()
            await self.uow.outbox.bulk_add(events)
            await self.uow.commit()
        return order


class StartOrderCommand(BaseCommand):
    order_id: PositiveInt


@dataclass(frozen=True)
class StartOrderCommandHandler(CommandHandler[StartOrderCommand, Order]):
    uow: SQLAlchemyScheduleUnitOfWork

    async def handle(self, command: StartOrderCommand) -> Order:
        async with self.uow:
            order = await self.uow.orders.find_one_or_none(id=command.order_id)
            if not order:
                raise OrderNotFoundLogicException(id=command.order_id)
            order.start()
            await self.uow.orders.update(entity=order)
            await self.uow.commit()
        return order


class PhotoType(BaseModel):
    file: BinaryIO | SpooledTemporaryFile
    filename: str
    content_type: str

    class Config:
        arbitrary_types_allowed = True


class UpdatePhotoOrderCommand(BaseCommand):
    order_id: PositiveInt
    photo_before: PhotoType
    photo_after: PhotoType


@dataclass(frozen=True)
class UpdatePhotoOrderCommandHandler(CommandHandler[UpdatePhotoOrderCommand, Order]):
    uow: SQLAlchemyScheduleUnitOfWork

    async def handle(self, command: UpdatePhotoOrderCommand) -> Order:
        async with self.uow:
            order = await self.uow.orders.find_one_or_none(id=command.order_id)
            if not order:
                raise OrderNotFoundLogicException(id=command.order_id)
            order.update_photo()
            order_from_repo = await self.uow.orders.update_photo(
                entity=order,
                photo_before=command.photo_before,
                photo_after=command.photo_after,
            )
            await self.uow.commit()
        return order_from_repo


class CancelOrderCommand(BaseCommand):
    order_id: PositiveInt
    user_id: PositiveInt


@dataclass(frozen=True)
class CancelOrderCommandHandler(CommandHandler[CancelOrderCommand, Order]):
    uow: SQLAlchemyScheduleUnitOfWork

    async def handle(self, command: CancelOrderCommand) -> Order:
        async with self.uow:
            order = await self.uow.orders.find_one_or_none(id=command.order_id)
            if not order:
                raise OrderNotFoundLogicException(id=command.order_id)
            elif not order.user_id == command.user_id:
                raise NotUserOrderLogicException()
            order.cancel()
            await self.uow.orders.update(order)
            logger.debug(f"{self.__class__.__name__}: uow.commit(); starting pulling events")
            events = order.pull_events()
            logger.debug(f"{self.__class__.__name__}: events: {events}, publushing ...")
            await self.uow.outbox.bulk_add(events)
            logger.debug(f"{self.__class__.__name__}: after mediator publish")
            await self.uow.commit()

        return order
