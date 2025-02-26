import asyncio

import aio_pika
import orjson as orjson

from src.domain.base.events import BaseEvent
from src.infrastructure.broker.converters import convert_event_to_broker_message
from src.infrastructure.broker.rabbit.connector import RabbitConnector
from src.infrastructure.logger_adapter.logger import init_logger
from src.presentation.api.settings import settings

logger = init_logger(__name__)


class Producer:
    def __init__(
        self,
        connector: RabbitConnector,
        # channel: AbstractRobustChannel
    ):
        self.connector = connector
        # self.channel = channel

    async def declare_exchange(self, exchange_name: str) -> None:
        async with self.connector:
            await self.connector.channel.declare_exchange(exchange_name, aio_pika.ExchangeType.DIRECT)

    async def publish_message(
        self,
        message_data: bytes,
        exchange_name: str,
        routing_key: str,
    ) -> None:
        rq_message = self.build_message(message_data)
        async with self.connector:
            exchange = await self.connector.channel.get_exchange(exchange_name, ensure=False)
            await exchange.publish(rq_message, routing_key=routing_key)
        logger.debug("Message sent", extra={"rq_message": rq_message})

    @staticmethod
    def build_message(message_data: bytes) -> aio_pika.Message:
        return aio_pika.Message(
            body=message_data,
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )


async def main():
    exchange_name = "user_create"
    routing_key = "user_create"
    c = RabbitConnector(settings)
    async with c:
        p = Producer(c)
        await p.declare_exchange(exchange_name)
        await p.publish_message(
            message_data=convert_event_to_broker_message(BaseEvent()),
            exchange_name=exchange_name,
            routing_key=routing_key,
        )


if __name__ == "__main__":
    asyncio.run(main())
