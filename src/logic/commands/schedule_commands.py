from dataclasses import dataclass
from datetime import date
from typing import Type

from pydantic import PositiveInt

from src.domain.base.values import BaseValueObject, CountNumber, Name
from src.domain.schedules.entities import Inventory, Master, Schedule
from src.logic.commands.base import BaseCommand, CommandHandler
from src.logic.exceptions.schedule_exceptions import (
    InventoryNotFoundLogicException,
    MasterNotFoundLogicException,
    ServiceNotFoundLogicException,
)
from src.logic.exceptions.user_exceptions import (
    UserNotFoundLogicException,
)
from src.logic.uows.schedule_uow import SQLAlchemyScheduleUnitOfWork


class DeleteScheduleCommand(BaseCommand):
    inventory_id: PositiveInt


class UpdateInventoryCommand(BaseCommand):
    inventory_id: PositiveInt
    name: str | None = None
    unit: str | None = None
    stock_count: PositiveInt | None = None


class AddInventoryCommand(BaseCommand):
    name: str
    unit: str
    stock_count: PositiveInt


class AddMasterCommand(BaseCommand):
    description: str
    user_id: PositiveInt
    services_id: list[PositiveInt]


class AddScheduleCommand(BaseCommand):
    day: date
    service_id: PositiveInt
    master_id: PositiveInt


@dataclass(frozen=True)
class DeleteScheduleCommandHandler(CommandHandler[DeleteScheduleCommand, None]):
    uow: SQLAlchemyScheduleUnitOfWork

    async def handle(self, command: DeleteScheduleCommand) -> None:
        inventory_id = command.inventory_id
        async with self.uow:
            inventory = await self.uow.inventories.find_one_or_none(id=inventory_id)
            if not inventory:
                raise InventoryNotFoundLogicException(inventory_id)
            await self.uow.inventories.delete(id=inventory_id)
            await self.uow.commit()


@dataclass(frozen=True)
class UpdateInventoryCommandCommandHandler(CommandHandler[UpdateInventoryCommand, None]):
    uow: SQLAlchemyScheduleUnitOfWork

    async def handle(self, command: UpdateInventoryCommand) -> None:
        async with self.uow:
            inventory = await self.uow.inventories.find_one_or_none(id=command.inventory_id)
            if not inventory:
                raise InventoryNotFoundLogicException(command.inventory_id)
            key_mapper: dict[str, Type[BaseValueObject]] = {
                "name": Name,
                "unit": Name,
                "stock_count": CountNumber,
            }
            for k, v in command.model_dump(exclude_none=True, exclude={"inventory_id"}).items():
                setattr(inventory, k, key_mapper.get(k)(value=v))
            inventory_from_repo = await self.uow.inventories.update(entity=inventory)
            await self.uow.commit()
            return inventory_from_repo


@dataclass(frozen=True)
class AddInventoryCommandCommandHandler(CommandHandler[AddInventoryCommand, None]):
    uow: SQLAlchemyScheduleUnitOfWork

    async def handle(self, command: AddInventoryCommand) -> None:
        async with self.uow:
            inventory = Inventory(
                name=Name(command.name),
                stock_count=CountNumber(command.stock_count),
                unit=Name(command.unit),
            )
            inventory_from_repo = await self.uow.inventories.add(entity=inventory)
            await self.uow.commit()
            return inventory_from_repo


@dataclass(frozen=True)
class AddMasterCommandCommandHandler(CommandHandler[AddMasterCommand, None]):
    uow: SQLAlchemyScheduleUnitOfWork

    async def handle(self, command: AddMasterCommand) -> None:
        async with self.uow:
            services = await self.uow.services.get_services_by_ids(command.services_id)
            if not services:
                raise ServiceNotFoundLogicException(id=command.services_id)
            user = await self.uow.users.find_one_or_none(id=command.user_id)
            if not user:
                raise UserNotFoundLogicException(id=command.user_id)
            master = Master(
                description=command.description,
                user=user,
                services=services,
            )
            master_from_repo = await self.uow.masters.add(entity=master)
            await self.uow.commit()
            return await self.uow.masters.find_one_or_none(id=master_from_repo.id)


@dataclass(frozen=True)
class AddScheduleCommandCommandHandler(CommandHandler[AddScheduleCommand, None]):
    uow: SQLAlchemyScheduleUnitOfWork

    async def handle(self, command: AddScheduleCommand):
        async with self.uow:
            service = await self.uow.services.find_one_or_none(id=command.service_id)
            if not service:
                raise ServiceNotFoundLogicException(id=command.service_id)
            master = await self.uow.masters.find_one_or_none(id=command.master_id)
            if not master:
                raise MasterNotFoundLogicException(id=command.master_id)
            schedule = Schedule(day=command.day, service=service, master=master)
            schedule_from_repo = await self.uow.schedules.add(entity=schedule)
            await self.uow.commit()
            return await self.uow.schedules.find_one_or_none(id=schedule_from_repo.id)
