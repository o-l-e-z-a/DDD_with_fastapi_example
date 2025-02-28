import asyncio

from dataclasses import dataclass
from pprint import pprint

import aio_pika

from src.infrastructure.broker.converters import convert_broker_message_to_dict
from src.logic.commands.order_commands import AddUserPointCommand, AddOrderPaymentCommand, UpdateUserPointCommand
from src.logic.event_consumers.base import BaseEventConsumer


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
            print(data_dict)
            cmd = AddUserPointCommand(**data_dict)
            user_point = (await self.mediator.handle_command(cmd))[0]
            print(f"user_point: {user_point}")
            # raise ValueError


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
            pprint(f"data_dict: {data_dict}")
            cmd = AddOrderPaymentCommand(**data_dict)
            order_payment = (await self.mediator.handle_command(cmd))[0]
            print(f"order_payment: {order_payment}")
            # raise ValueError


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
            pprint(f"data_dict: {data_dict}")
            point_to_operation = data_dict.get("point_uses")
            user_point_id = data_dict.get("user_point_id")
            operation = "-"
            cmd = UpdateUserPointCommand(
                user_point_id=user_point_id, point_to_operation=point_to_operation, operation=operation
            )
            user_point = (await self.mediator.handle_command(cmd))[0]
            print(f"user_point: {user_point}")
