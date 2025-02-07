from dataclasses import dataclass
from datetime import date
from typing import Annotated

from pydantic import Field, PositiveInt

from src.domain.base.values import Name, PositiveIntNumber
from src.domain.orders.entities import Promotion
from src.logic.commands.base import BaseCommand, CommandHandler
from src.logic.exceptions.schedule_exceptions import ServiceNotFoundLogicException
from src.logic.uows.order_uow import SQLAlchemyOrderUnitOfWork

int_ge_0 = Annotated[int, Field(ge=0)]


class TotalAmountDTO(BaseCommand):
    schedule_id: int
    point: int_ge_0 | None = 0
    promotion_code: str | None = "0"


class AddPromotionCommand(BaseCommand):
    code: str = Field(..., max_length=15)
    sale: int = Field(..., ge=0, lt=100)
    is_active: bool = True
    day_start: date
    day_end: date
    services_id: list[int]


@dataclass(frozen=True)
class AddPromotionCommandCommandHandler(CommandHandler[AddPromotionCommand, None]):
    uow: SQLAlchemyOrderUnitOfWork

    async def handle(self, command: AddPromotionCommand) -> None:
        async with self.uow:
            services = await self.uow.services.get_services_by_ids(command.promotion_data.services_id)
            if not services:
                raise ServiceNotFoundLogicException(id=command.promotion_data.services_id)
            promotion = Promotion(
                code=Name(command.promotion_data.code),
                sale=PositiveIntNumber(command.promotion_data.sale),
                is_active=command.promotion_data.is_active,
                day_start=command.promotion_data.day_start,
                day_end=command.promotion_data.day_end,
                services=services,
            )
            promotion_from_repo = await self.uow.promotions.add(entity=promotion)
            await self.uow.commit()
            return await self.uow.promotions.find_one_or_none(id=promotion_from_repo.id)


class UpdatePromotionCommand(AddPromotionCommand):
    promotion_id: PositiveInt


@dataclass(frozen=True)
class UpdatePromotionCommandCommandHandler(CommandHandler[UpdatePromotionCommand, None]):
    uow: SQLAlchemyOrderUnitOfWork

    async def handle(self, command: UpdatePromotionCommand) -> None:
        async with self.uow:
            services = await self.uow.services.get_services_by_ids(command.promotion_data.services_id)
            if not services:
                raise ServiceNotFoundLogicException(id=command.promotion_data.services_id)
            promotion = Promotion(
                code=Name(command.promotion_data.code),
                sale=PositiveIntNumber(command.promotion_data.sale),
                is_active=command.promotion_data.is_active,
                day_start=command.promotion_data.day_start,
                day_end=command.promotion_data.day_end,
                services=services,
            )
            promotion_from_repo = await self.uow.promotions.add(entity=promotion)
            await self.uow.commit()
            return await self.uow.promotions.find_one_or_none(id=promotion_from_repo.id)


class DeletePromotionCommand(BaseCommand):
    promotion_id: PositiveInt


@dataclass(frozen=True)
class DeletePromotionCommandCommandHandler(CommandHandler[DeletePromotionCommand, None]):
    uow: SQLAlchemyOrderUnitOfWork

    async def handle(self, command: DeletePromotionCommand) -> None:
        async with self.uow:
            services = await self.uow.services.get_services_by_ids(command.promotion_data.services_id)
            if not services:
                raise ServiceNotFoundLogicException(id=command.promotion_data.services_id)
            promotion = Promotion(
                code=Name(command.promotion_data.code),
                sale=PositiveIntNumber(command.promotion_data.sale),
                is_active=command.promotion_data.is_active,
                day_start=command.promotion_data.day_start,
                day_end=command.promotion_data.day_end,
                services=services,
            )
            promotion_from_repo = await self.uow.promotions.add(entity=promotion)
            await self.uow.commit()
            return await self.uow.promotions.find_one_or_none(id=promotion_from_repo.id)
