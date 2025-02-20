from dataclasses import dataclass
from datetime import date
from typing import Annotated

from pydantic import Field, PositiveInt

from src.domain.base.values import Name, PositiveIntNumber
from src.domain.orders.entities import Promotion
from src.logic.commands.base import BaseCommand, CommandHandler
from src.logic.exceptions.order_exceptions import PromotionNotFoundLogicException
from src.logic.exceptions.schedule_exceptions import ServiceNotFoundLogicException
from src.infrastructure.db.uows.order_uow import SQLAlchemyOrderUnitOfWork

int_ge_0 = Annotated[int, Field(ge=0)]


class AddPromotionCommand(BaseCommand):
    code: str = Field(..., max_length=15)
    sale: int = Field(..., ge=0, lt=100)
    is_active: bool = True
    day_start: date
    day_end: date
    services_id: list[int]


@dataclass(frozen=True)
class AddPromotionCommandCommandHandler(CommandHandler[AddPromotionCommand, Promotion]):
    uow: SQLAlchemyOrderUnitOfWork

    async def handle(self, command: AddPromotionCommand) -> Promotion:
        async with self.uow:
            services = await self.uow.services.get_services_by_ids(command.services_id)
            if not services:
                raise ServiceNotFoundLogicException(id=command.services_id)
            promotion = Promotion(
                code=Name(command.code),
                sale=PositiveIntNumber(command.sale),
                is_active=command.is_active,
                day_start=command.day_start,
                day_end=command.day_end,
                services_id=command.services_id,
            )
            promotion_from_repo = await self.uow.promotions.add(entity=promotion)
            await self.uow.commit()
            return promotion_from_repo


class UpdatePromotionCommand(AddPromotionCommand):
    promotion_id: PositiveInt


@dataclass(frozen=True)
class UpdatePromotionCommandCommandHandler(CommandHandler[UpdatePromotionCommand, Promotion]):
    uow: SQLAlchemyOrderUnitOfWork

    async def handle(self, command: UpdatePromotionCommand) -> Promotion:
        async with self.uow:
            promotion = await self.uow.promotions.find_one_or_none(id=command.promotion_id)
            if not promotion:
                raise PromotionNotFoundLogicException(id=command.promotion_id)
            services = await self.uow.services.get_services_by_ids(command.services_id)
            if not services:
                raise ServiceNotFoundLogicException(id=command.services_id)
            promotion.code = Name(command.code)
            promotion.sale = PositiveIntNumber(command.sale)
            promotion.is_active = command.is_active
            promotion.day_start = command.day_start
            promotion.day_end = command.day_end
            promotion.services = services
            promotion_from_repo = await self.uow.promotions.update(entity=promotion)
            await self.uow.commit()
            return promotion_from_repo


class DeletePromotionCommand(BaseCommand):
    promotion_id: PositiveInt


@dataclass(frozen=True)
class DeletePromotionCommandCommandHandler(CommandHandler[DeletePromotionCommand, Promotion]):
    uow: SQLAlchemyOrderUnitOfWork

    async def handle(self, command: DeletePromotionCommand) -> None:
        async with self.uow:
            promotion = await self.uow.promotions.find_one_or_none(id=command.promotion_id)
            if not promotion:
                raise PromotionNotFoundLogicException(id=command.promotion_id)
            await self.uow.promotions.delete(id=command.promotion_id)
            await self.uow.commit()
