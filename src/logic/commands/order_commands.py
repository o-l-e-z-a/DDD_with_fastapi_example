from dataclasses import dataclass
from datetime import date
from typing import Annotated, Literal

from pydantic import Field, PositiveInt

from src.domain.base.values import Name, PositiveIntNumber
from src.domain.orders.entities import OrderPayment, Promotion, UserPoint
from src.domain.orders.service import TotalAmountResult
from src.infrastructure.db.uows.order_uow import SQLAlchemyOrderUnitOfWork
from src.infrastructure.logger_adapter.logger import init_logger
from src.infrastructure.other_service_integration.schedule_service import ScheduleServiceIntegration
from src.logic.commands.base import BaseCommand, CommandHandler
from src.logic.events.order_events import OrderPayedEvent, OrderPaymentCanceledEvent
from src.logic.exceptions.order_exceptions import (
    OrderPaymentNotFoundLogicException,
    PromotionNotFoundLogicException,
    UserPointNotFoundLogicException,
)
from src.logic.exceptions.schedule_exceptions import OrderNotFoundLogicException, ServiceNotFoundLogicException
from src.logic.exceptions.user_exceptions import UserNotFoundLogicException

logger = init_logger(__name__)
int_ge_0 = Annotated[int, Field(ge=0)]


class AddUserPointCommand(BaseCommand):
    user_id: PositiveInt


@dataclass(frozen=True)
class AddUserPointCommandHandler(CommandHandler[AddUserPointCommand, UserPoint]):
    uow: SQLAlchemyOrderUnitOfWork

    async def handle(self, command: AddUserPointCommand) -> UserPoint:
        async with self.uow:
            user = await self.uow.users.find_one_or_none(id=command.user_id)
            if not user:
                raise UserNotFoundLogicException(id=command.user_id)
            user_point = UserPoint(
                user_id=command.user_id,
            )
            user_point_from_repo = await self.uow.user_points.add(entity=user_point)
            await self.uow.commit()
        return user_point_from_repo


class AddOrderPaymentCommand(BaseCommand):
    order_id: PositiveInt
    service_price: PositiveInt


@dataclass(frozen=True)
class AddOrderPaymentCommandHandler(CommandHandler[AddOrderPaymentCommand, OrderPayment]):
    uow: SQLAlchemyOrderUnitOfWork
    schedule_client: ScheduleServiceIntegration

    async def handle(self, command: AddOrderPaymentCommand) -> OrderPayment:
        async with self.uow:
            order = await self.schedule_client.get_order_by_id(order_id=command.order_id)
            if not order:
                logger.error("OrderNotFoundLogicException with order: {command.order_i}")
                raise OrderNotFoundLogicException(id=command.order_id)
            order_payment = OrderPayment.add(order_id=command.order_id, service_price=command.service_price)
            order_payment_from_repo = await self.uow.order_payments.add(entity=order_payment)
            await self.uow.commit()
        return order_payment_from_repo


class OrderPayCommand(BaseCommand):
    order_payment_id: PositiveInt
    user_id: PositiveInt
    input_point: int_ge_0 | None = 0
    promotion_code: str | None = "0"


@dataclass(frozen=True)
class OrderPayCommandHandler(CommandHandler[OrderPayCommand, OrderPayment]):
    uow: SQLAlchemyOrderUnitOfWork

    async def handle(self, command: OrderPayCommand) -> OrderPayment:
        async with self.uow:
            order_payment = await self.uow.order_payments.find_one_or_none(id=command.order_payment_id)
            if not order_payment:
                raise OrderPaymentNotFoundLogicException(id=command.order_payment_id)
            promotion = await self.uow.promotions.find_one_or_none(code=command.promotion_code)
            user_point = await self.uow.user_points.find_one_or_none(user_id=command.user_id)
            promotion_sale = promotion.sale.as_generic_type() if promotion else None
            user_point_count = user_point.count.as_generic_type() if user_point else None
            order_payment.pay(
                promotion_sale=promotion_sale,
                user_point_count=user_point_count,
                input_user_point=command.input_point,
            )
            await self.uow.order_payments.update(entity=order_payment)
            logger.debug(f"{self.__class__.__name__}: uow.commit(); starting pulling events")
            events = order_payment.pull_events()
            if order_payment.point_uses:
                payed_event = OrderPayedEvent(
                    order_payment_id=order_payment.id,
                    user_point_id=user_point.id,
                    point_uses=order_payment.point_uses.as_generic_type(),
                )
                events.append(payed_event)
                logger.debug(f"{self.__class__.__name__}: events: {events}, publushing ...")
                await self.uow.outbox.bulk_add(events)
                logger.debug(f"{self.__class__.__name__}: after mediator publish")
            await self.uow.commit()
        return order_payment


class OrderPaymentCancelCommand(BaseCommand):
    order_id: PositiveInt
    user_id: PositiveInt


@dataclass(frozen=True)
class OrderPaymentCancelCommandHandler(CommandHandler[OrderPaymentCancelCommand, OrderPayment]):
    uow: SQLAlchemyOrderUnitOfWork

    async def handle(self, command: OrderPaymentCancelCommand) -> OrderPayment:
        async with self.uow:
            order_payment = await self.uow.order_payments.find_one_or_none(order_id=command.order_id)
            if not order_payment:
                raise OrderPaymentNotFoundLogicException(id=command.order_id)
            user_point = await self.uow.user_points.find_one_or_none(user_id=command.user_id)
            order_payment.cancel_payment()
            await self.uow.order_payments.update(entity=order_payment)
            logger.debug(f"{self.__class__.__name__}: uow.commit(), starting pulling events")
            events = order_payment.pull_events()
            if order_payment.point_uses:
                payed_event = OrderPaymentCanceledEvent(
                    order_payment_id=order_payment.id,
                    user_point_id=user_point.id,
                    point_uses=order_payment.point_uses.as_generic_type(),
                )
                events.append(payed_event)
                logger.debug(f"{self.__class__.__name__}: events: {events}, publushing ...")
                await self.uow.outbox.bulk_add(events)
                logger.debug(f"{self.__class__.__name__}: after mediator publish")
            await self.uow.commit()
        return order_payment


class UpdateUserPointCommand(BaseCommand):
    user_point_id: int
    point_to_operation: int
    operation: Literal["+", "-"]


@dataclass(frozen=True)
class UpdateUserPointCommandHandler(CommandHandler[UpdateUserPointCommand, UserPoint]):
    uow: SQLAlchemyOrderUnitOfWork

    async def handle(self, command: UpdateUserPointCommand) -> UserPoint:
        async with self.uow:
            user_point = await self.uow.user_points.find_one_or_none(id=command.user_point_id)
            if not user_point:
                raise UserPointNotFoundLogicException(id=command.user_point_id)
            user_point.update(operation=command.operation, point_to_operation=command.point_to_operation)
            await self.uow.user_points.update(entity=user_point)
            await self.uow.commit()
        logger.debug(f"{self.__class__.__name__}: uow.commit()")
        return user_point


class CalculateOrderCommand(BaseCommand):
    order_payment_id: PositiveInt
    user_id: PositiveInt
    input_point: int_ge_0 | None = 0
    promotion_code: str | None = "0"


@dataclass(frozen=True)
class CalculateOrderCommandHandler(CommandHandler[CalculateOrderCommand, TotalAmountResult]):
    uow: SQLAlchemyOrderUnitOfWork

    async def handle(self, command: CalculateOrderCommand) -> TotalAmountResult:
        async with self.uow:
            order_payment = await self.uow.order_payments.find_one_or_none(id=command.order_payment_id)
            if not order_payment:
                raise OrderPaymentNotFoundLogicException(id=command.order_payment_id)
            promotion = await self.uow.promotions.find_one_or_none(code=command.promotion_code)
            user_point = await self.uow.user_points.find_one_or_none(user_id=command.user_id)
            promotion_sale = promotion.sale.as_generic_type() if promotion else None
            user_point_count = user_point.count.as_generic_type() if user_point else None
            amount_result = order_payment.calculate_amount(
                promotion_sale=promotion_sale,
                user_point_count=user_point_count,
                input_user_point=command.input_point,
            )
            return amount_result


# Promotions
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
    schedule_client: ScheduleServiceIntegration

    async def handle(self, command: AddPromotionCommand) -> Promotion:
        async with self.uow:
            services_id = await self.schedule_client.get_services_id_only(command.services_id)
            for service_id in command.services_id:
                if service_id not in services_id:
                    raise ServiceNotFoundLogicException(id=service_id)
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
    schedule_client: ScheduleServiceIntegration

    async def handle(self, command: UpdatePromotionCommand) -> Promotion:
        async with self.uow:
            promotion = await self.uow.promotions.find_one_or_none(id=command.promotion_id)
            if not promotion:
                raise PromotionNotFoundLogicException(id=command.promotion_id)
            services_id = await self.schedule_client.get_services_id_only(command.services_id)
            for service_id in command.services_id:
                if service_id not in services_id:
                    raise ServiceNotFoundLogicException(id=service_id)
            promotion.code = Name(command.code)
            promotion.sale = PositiveIntNumber(command.sale)
            promotion.is_active = command.is_active
            promotion.day_start = command.day_start
            promotion.day_end = command.day_end
            promotion.services_id = command.services_id
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
