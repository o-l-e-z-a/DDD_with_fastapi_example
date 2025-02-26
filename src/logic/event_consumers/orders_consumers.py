import asyncio

from dataclasses import dataclass

import aio_pika

from src.domain.orders.entities import UserPoint
from src.infrastructure.broker.converters import convert_broker_message_to_dict
from src.logic.commands.order_commands import AdduserPointCommand
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
            cmd = AdduserPointCommand(**data_dict)
            user_point: UserPoint = (await self.mediator.handle_command(cmd))[0]
            print(f"user_point: {user_point}")
            await asyncio.sleep(1)
            # raise ValueError
