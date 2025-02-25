from dataclasses import dataclass
from datetime import date
from typing import Annotated

from pydantic import Field, PositiveInt

from src.domain.base.values import Name, PositiveIntNumber
from src.domain.orders.entities import Promotion
from src.domain.orders.service import TotalAmountResult
from src.infrastructure.db.uows.order_uow import SQLAlchemyOrderUnitOfWork
from src.logic.commands.base import BaseCommand, CommandHandler
from src.logic.exceptions.order_exceptions import OrderNotFoundLogicException, PromotionNotFoundLogicException
from src.logic.exceptions.schedule_exceptions import ServiceNotFoundLogicException

int_ge_0 = Annotated[int, Field(ge=0)]


class AddPromotionCommand(BaseCommand):
    code: str = Field(..., max_length=15)
    sale: int = Field(..., ge=0, lt=100)
    is_active: bool = True
    day_start: date
    day_end: date
    services_id: list[int]


@dataclass(frozen=True)
class AddPromotionCommandHandler(CommandHandler[AddPromotionCommand, Promotion]):
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
class UpdatePromotionCommandHandler(CommandHandler[UpdatePromotionCommand, Promotion]):
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
class DeletePromotionCommandHandler(CommandHandler[DeletePromotionCommand, Promotion]):
    uow: SQLAlchemyOrderUnitOfWork

    async def handle(self, command: DeletePromotionCommand) -> None:
        async with self.uow:
            promotion = await self.uow.promotions.find_one_or_none(id=command.promotion_id)
            if not promotion:
                raise PromotionNotFoundLogicException(id=command.promotion_id)
            await self.uow.promotions.delete(id=command.promotion_id)
            await self.uow.commit()


class CalculateOrderCommand(BaseCommand):
    order_id: PositiveInt
    user_id: PositiveInt
    input_point: int_ge_0 | None = 0
    promotion_code: str | None = "0"


@dataclass(frozen=True)
class CalculateOrderCommandHandler(CommandHandler[CalculateOrderCommand, TotalAmountResult]):
    uow: SQLAlchemyOrderUnitOfWork

    async def handle(self, command: CalculateOrderCommand) -> TotalAmountResult:
        async with self.uow:
            order = await self.uow.orders.find_one_or_none(id=command.order_id)
            if not order:
                raise OrderNotFoundLogicException(id=command.order_id)
            promotion = await self.uow.promotions.find_one_or_none(code=command.promotion_code)
            user_point = await self.uow.user_points.find_one_or_none(user_id=command.user_id)
            promotion_sale = promotion.sale.as_generic_type() if promotion else None
            user_point_count = user_point.count.as_generic_type() if user_point else None
            amount_result = order.calculate_amount(
                promotion_sale=promotion_sale,
                user_point_count=user_point_count,
                input_user_point=command.input_point,
            )
            return amount_result
