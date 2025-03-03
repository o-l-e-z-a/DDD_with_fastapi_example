import asyncio

from typing import Any, Callable

import aio_pika

from aio_pika.abc import AbstractIncomingMessage, AbstractRobustQueue, ExchangeType

from src.infrastructure.broker.converters import convert_broker_message_to_dict
from src.infrastructure.broker.rabbit.connector import RabbitConnector
from src.infrastructure.logger_adapter.logger import init_logger

logger = init_logger(__name__)


class RabbitConsumer:
    def __init__(
        self,
        connector: RabbitConnector,
        # channel: AbstractRobustChannel
    ):
        self.connector = connector
        # self.channel = channel

    async def declare_queue(
        self,
        channel,
        exchange_name: str,
        queue_name: str,
        routing_key: str,
    ) -> AbstractRobustQueue:
        exchange = await channel.declare_exchange(
            name=exchange_name,
            type=ExchangeType.DIRECT,
        )
        queue = await channel.declare_queue(name=queue_name, durable=True)
        await queue.bind(exchange=exchange, routing_key=routing_key)
        return queue

    async def consume_messages(
        self,
        message_callback: Callable[[AbstractIncomingMessage], Any],
        exchange_name: str,
        queue_name: str,
        routing_key: str,
    ):
        async with self.connector:
            queue = await self.declare_queue(
                channel=self.connector.channel,
                exchange_name=exchange_name,
                queue_name=queue_name,
                routing_key=routing_key,
            )
            await queue.consume(
                callback=message_callback,
            )
            logger.info("Waiting for messages...")

            await asyncio.Future()

    # async def consume_messages(
    #     self,
    #     message_callback: Callable[[AbstractIncomingMessage], Any],
    #     exchange_name: str,
    #     queue_name: str,
    #     routing_key: str,
    # ):
    #     queue = await self.declare_queue(
    #         channel=self.channel,
    #         exchange_name=exchange_name,
    #         queue_name=queue_name,
    #         routing_key=routing_key,
    #     )
    #     await queue.consume(
    #         callback=message_callback,
    #     )
    #     logger.warning("Waiting for messages...")
    #
    #     await asyncio.Future()


async def process_new_message(
    message: aio_pika.abc.AbstractIncomingMessage,
) -> None:
    print("Processing new message")
    async with message.process():
        print(convert_broker_message_to_dict(message.body))
        await asyncio.sleep(1)
        print()
        # raise ValueError


async def main():
    pass
    # c = RabbitConnector(settings)
    # p = RabbitConsumer(c)
    # callback = UserCreatedCallback()
    # await p.consume_messages(
    #     callback,
    #     queue_name=callback.queue_name,
    #     exchange_name=callback.exchange_name,
    #     routing_key=callback.routing_key
    # )
    # await p.declare_exchange(exchange_name)
    # await p.publish_message(
    #         message_data=convert_event_to_broker_message("adasdasdasdasd"),
    #         exchange_name=exchange_name,
    #         routing_key=routing_key
    # )


if __name__ == "__main__":
    asyncio.run(main())
