from dataclasses import dataclass

import aio_pika

from src.infrastructure.broker.converters import convert_broker_message_to_dict
from src.infrastructure.logger_adapter.logger import init_logger
from src.logic.commands.order_commands import (
    AddOrderPaymentCommand,
    AddUserPointCommand,
    OrderPaymentCancelCommand,
    UpdateUserPointCommand,
)
from src.logic.event_consumers.base import BaseEventConsumer

logger = init_logger(__name__)


@dataclass(frozen=True)
class UserCreatedEventConsumer(BaseEventConsumer):
    exchange_name = "user_create"
    queue_name = "user_create"
    routing_key = "user_create"

    async def __call__(
        self,
        message: aio_pika.abc.AbstractIncomingMessage,
    ) -> None:
        async with message.process():
            data_dict = convert_broker_message_to_dict(message.body)
            cmd = AddUserPointCommand(**data_dict)
            logger.debug(f"{self.__class__.__name__}: принял {self.routing_key} event: start cmd {cmd}")
            results: list = await self.mediator.handle_command(cmd)
            logger.debug(f"{self.__class__.__name__}: result after mediator: {results}")


@dataclass(frozen=True)
class OrderCreatedEventConsumer(BaseEventConsumer):
    exchange_name = "order_create"
    queue_name = "order_create"
    routing_key = "order_create"

    async def __call__(
        self,
        message: aio_pika.abc.AbstractIncomingMessage,
    ) -> None:
        async with message.process():
            data_dict = convert_broker_message_to_dict(message.body)
            cmd = AddOrderPaymentCommand(**data_dict)
            logger.debug(f"{self.__class__.__name__}: принял {self.routing_key} event: start cmd {cmd}")
            results: list = await self.mediator.handle_command(cmd)
            logger.debug(f"{self.__class__.__name__}: result after mediator: {results}")


@dataclass(frozen=True)
class OrderPayedEventConsumer(BaseEventConsumer):
    exchange_name = "order_payed"
    queue_name = "order_payed"
    routing_key = "order_payed"

    async def __call__(
        self,
        message: aio_pika.abc.AbstractIncomingMessage,
    ) -> None:
        async with message.process():
            data_dict = convert_broker_message_to_dict(message.body)
            point_to_operation = data_dict.get("point_uses")
            user_point_id = data_dict.get("user_point_id")
            operation = "-"
            cmd = UpdateUserPointCommand(
                user_point_id=user_point_id, point_to_operation=point_to_operation, operation=operation
            )
            logger.debug(f"{self.__class__.__name__}: принял {self.routing_key} event: start cmd {cmd}")
            results: list = await self.mediator.handle_command(cmd)
            logger.debug(f"{self.__class__.__name__}: result after mediator: {results}")


@dataclass(frozen=True)
class OrderCancelledEventConsumer(BaseEventConsumer):
    exchange_name = "order_cancel"
    queue_name = "order_cancel"
    routing_key = "order_cancel"

    async def __call__(
        self,
        message: aio_pika.abc.AbstractIncomingMessage,
    ) -> None:
        async with message.process():
            data_dict = convert_broker_message_to_dict(message.body)
            cmd = OrderPaymentCancelCommand(**data_dict)
            logger.debug(f"{self.__class__.__name__}: принял {self.routing_key} event: start cmd {cmd}")
            results: list = await self.mediator.handle_command(cmd)
            logger.debug(f"{self.__class__.__name__}: result after mediator: {results}")


@dataclass(frozen=True)
class OrderPaymentCancelledEventConsumer(BaseEventConsumer):
    exchange_name = "order_payment_cancel"
    queue_name = "order_payment_cancel"
    routing_key = "order_payment_cancel"

    async def __call__(
        self,
        message: aio_pika.abc.AbstractIncomingMessage,
    ) -> None:
        async with message.process():
            data_dict = convert_broker_message_to_dict(message.body)
            point_to_operation = data_dict.get("point_uses")
            user_point_id = data_dict.get("user_point_id")
            operation = "+"
            cmd = UpdateUserPointCommand(
                user_point_id=user_point_id, point_to_operation=point_to_operation, operation=operation
            )
            logger.debug(f"{self.__class__.__name__}: принял {self.routing_key} event: start cmd {cmd}")
            results: list = await self.mediator.handle_command(cmd)
            logger.debug(f"{self.__class__.__name__}: result after mediator: {results}")
