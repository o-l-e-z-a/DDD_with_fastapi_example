from dataclasses import dataclass
from datetime import date
from typing import Annotated

from pydantic import Field, PositiveInt

from src.domain.schedules.entities import Master, Order, Schedule
from src.logic.commands.base import BaseCommand, CommandHandler
from src.logic.dto.order_dto import PhotoDTO
from src.logic.exceptions.order_exceptions import NotUserOrderLogicException, OrderNotFoundLogicException
from src.logic.exceptions.schedule_exceptions import (
    MasterNotFoundLogicException,
    ServiceNotFoundLogicException,
    SlotNotFoundLogicException,
)
from src.logic.exceptions.user_exceptions import UserNotFoundLogicException
from src.logic.uows.schedule_uow import SQLAlchemyScheduleUnitOfWork


class AddMasterCommand(BaseCommand):
    description: str
    user_id: PositiveInt
    services_id: list[PositiveInt]


@dataclass(frozen=True)
class AddMasterCommandHandler(CommandHandler[AddMasterCommand, None]):
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
            print(master_from_repo, master_from_repo.id)
            await self.uow.commit()
            # return await self.uow.masters.find_one_or_none(id=master_from_repo.id)
            return master_from_repo


class AddScheduleCommand(BaseCommand):
    day: date
    master_id: PositiveInt


@dataclass(frozen=True)
class AddScheduleCommandHandler(CommandHandler[AddScheduleCommand, None]):
    uow: SQLAlchemyScheduleUnitOfWork

    async def handle(self, command: AddScheduleCommand) -> Schedule:
        async with self.uow:
            master = await self.uow.masters.find_one_or_none(id=command.master_id)
            if not master:
                raise MasterNotFoundLogicException(id=command.master_id)
            schedule = Schedule.add(day=command.day, master_id=command.master_id)
            schedule_from_repo = await self.uow.schedules.add(entity=schedule)
            await self.uow.commit()
            # return await self.uow.schedules.find_one_or_none(id=schedule_from_repo.id)
            return schedule_from_repo


slot_type = Annotated[str, Field(pattern=r"^(?:[01][0-9]|2?[0-3]):[0-5]\d$")]


class AddOrderCommand(BaseCommand):
    # total_amount: TotalAmountDTO
    slot_id: PositiveInt
    service_id: PositiveInt
    user_id: PositiveInt


@dataclass(frozen=True)
class AddOrderCommandHandler(CommandHandler[AddOrderCommand, None]):
    uow: SQLAlchemyScheduleUnitOfWork

    async def handle(self, command: AddOrderCommand) -> Order:
        async with self.uow:
            service = await self.uow.services.find_one_or_none(id=command.service_id)
            if not service:
                raise ServiceNotFoundLogicException(id=command.service_id)
            slot = await self.uow.schedules.find_one_or_none_slot(slot_id=command.slot_id)
            if not slot:
                raise SlotNotFoundLogicException(id=command.slot_id)
            schedule_master_services = await self.uow.schedules.find_master_services_by_schedule(
                schedule_id=slot.schedule_id
            )
            occupied_slots = await self.uow.schedules.find_occupied_slots(schedule_id=slot.schedule_id)
            order_from_aggregate = Order.add(
                user_id=command.user_id,
                service_id=command.service_id,
                slot_id=command.slot_id,
                schedule_master_services_id=schedule_master_services,
                occupied_slots=occupied_slots,
            )
            order_from_repo = await self.uow.orders.add(order_from_aggregate)
            # await self.uow.commit()
            events = order_from_aggregate.pull_events()
            print("events", events)
            await self.mediator.publish(events)
            return order_from_repo


class UpdateOrderCommand(BaseCommand):
    order_id: PositiveInt
    slot_id: PositiveInt
    user_id: PositiveInt


@dataclass(frozen=True)
class UpdateOrderCommandHandler(CommandHandler[UpdateOrderCommand, None]):
    uow: SQLAlchemyScheduleUnitOfWork

    async def handle(self, command: UpdateOrderCommand) -> None:
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
            await self.uow.commit()
            events = order.pull_events()
            print("events", events)
            await self.mediator.publish(events)
            return order


class StartOrderCommand(BaseCommand):
    order_id: PositiveInt


@dataclass(frozen=True)
class StartOrderCommandHandler(CommandHandler[StartOrderCommand, None]):
    uow: SQLAlchemyScheduleUnitOfWork

    async def handle(self, command: StartOrderCommand) -> None:
        async with self.uow:
            order = await self.uow.orders.find_one_or_none(id=command.order_id)
            if not order:
                raise OrderNotFoundLogicException(id=command.order_id)
            order.start()
            await self.uow.orders.update(entity=order)
            await self.uow.commit()
            return order


class UpdatePhotoOrderCommand(BaseCommand):
    order_id: PositiveInt
    photo_before: PhotoDTO
    photo_after: PhotoDTO


@dataclass(frozen=True)
class UpdatePhotoOrderCommandHandler(CommandHandler[UpdatePhotoOrderCommand, None]):
    uow: SQLAlchemyScheduleUnitOfWork

    async def handle(self, command: UpdatePhotoOrderCommand) -> None:
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
class CancelOrderCommandHandler(CommandHandler[CancelOrderCommand, None]):
    uow: SQLAlchemyScheduleUnitOfWork

    async def handle(self, command: CancelOrderCommand) -> None:
        async with self.uow:
            order = await self.uow.orders.find_one_or_none(id=command.order_id)
            if not order:
                raise OrderNotFoundLogicException(id=command.order_id)
            elif not order.user_id == command.user_id:
                raise NotUserOrderLogicException()

            order.cancel()
            await self.uow.orders.update(order)
            await self.uow.commit()
            return order


# class DeleteScheduleCommand(BaseCommand):
#     inventory_id: PositiveInt
#
#
# class UpdateInventoryCommand(BaseCommand):
#     inventory_id: PositiveInt
#     name: str | None = None
#     unit: str | None = None
#     stock_count: PositiveInt | None = None
#
#
# class AddInventoryCommand(BaseCommand):
#     name: str
#     unit: str
#     stock_count: PositiveInt


# @dataclass(frozen=True)
# class DeleteScheduleCommandHandler(CommandHandler[DeleteScheduleCommand, None]):
#     uow: SQLAlchemyScheduleUnitOfWork
#
#     async def handle(self, command: DeleteScheduleCommand) -> None:
#         inventory_id = command.inventory_id
#         async with self.uow:
#             inventory = await self.uow.inventories.find_one_or_none(id=inventory_id)
#             if not inventory:
#                 raise InventoryNotFoundLogicException(inventory_id)
#             await self.uow.inventories.delete(id=inventory_id)
#             await self.uow.commit()
#
#
# @dataclass(frozen=True)
# class UpdateInventoryCommandCommandHandler(CommandHandler[UpdateInventoryCommand, None]):
#     uow: SQLAlchemyScheduleUnitOfWork
#
#     async def handle(self, command: UpdateInventoryCommand) -> None:
#         async with self.uow:
#             inventory = await self.uow.inventories.find_one_or_none(id=command.inventory_id)
#             if not inventory:
#                 raise InventoryNotFoundLogicException(command.inventory_id)
#             key_mapper: dict[str, Type[BaseValueObject]] = {
#                 "name": Name,
#                 "unit": Name,
#                 "stock_count": CountNumber,
#             }
#             for k, v in command.model_dump(exclude_none=True, exclude={"inventory_id"}).items():
#                 setattr(inventory, k, key_mapper.get(k)(value=v))
#             inventory_from_repo = await self.uow.inventories.update(entity=inventory)
#             await self.uow.commit()
#             return inventory_from_repo
#
#
# @dataclass(frozen=True)
# class AddInventoryCommandCommandHandler(CommandHandler[AddInventoryCommand, None]):
#     uow: SQLAlchemyScheduleUnitOfWork
#
#     async def handle(self, command: AddInventoryCommand) -> None:
#         async with self.uow:
#             inventory = Inventory(
#                 name=Name(command.name),
#                 stock_count=CountNumber(command.stock_count),
#                 unit=Name(command.unit),
#             )
#             inventory_from_repo = await self.uow.inventories.add(entity=inventory)
#             await self.uow.commit()
#             return inventory_from_repo
