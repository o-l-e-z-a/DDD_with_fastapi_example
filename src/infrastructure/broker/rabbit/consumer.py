import asyncio

from typing import Any, Callable

import aio_pika

from aio_pika.abc import AbstractIncomingMessage, AbstractRobustChannel, AbstractRobustQueue, ExchangeType

from src.infrastructure.broker.converters import convert_broker_message_to_dict
from src.infrastructure.broker.rabbit.connector import RabbitConnector, except_rabbit_exception_deco
from src.infrastructure.logger_adapter.logger import init_logger

logger = init_logger(__name__)


class RabbitConsumer:
    def __init__(
        self,
        connector: RabbitConnector,
    ):
        self.connector = connector

    @except_rabbit_exception_deco
    async def declare_queue(
        self,
        channel: AbstractRobustChannel,
        exchange_name: str,
        queue_name: str,
        routing_key: str,
    ) -> AbstractRobustQueue:
        dlx_name = f"{exchange_name}_dlx"
        dlq_name = f"{queue_name}_dlq"
        dlx = await channel.declare_exchange(
            name=dlx_name,
            type=ExchangeType.FANOUT,
            # type=ExchangeType.X_DELAYED_MESSAGE,
            # arguments={
            #     "x-delayed-type": "direct"
            # }
        )
        dlq = await channel.declare_queue(
            name=dlq_name,
            durable=True,
            arguments={
                # "x-delay": 5 * 1000,
                "x-dead-letter-exchange": exchange_name,
                "x-message-ttl": 60 * 1000,
            },
        )
        await dlq.bind(exchange=dlx)
        exchange = await channel.declare_exchange(
            name=exchange_name,
            type=ExchangeType.DIRECT,
        )
        queue = await channel.declare_queue(
            name=queue_name,
            durable=True,
            arguments={
                "x-dead-letter-exchange": dlx_name,
                # "x-dead-routing-key": routing_key,
            },
        )
        await queue.bind(exchange=exchange, routing_key=routing_key)
        return queue

    @except_rabbit_exception_deco
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


async def process_new_message(
    message: aio_pika.abc.AbstractIncomingMessage,
) -> None:
    logger.debug("Start processing new message")
    async with message.process():
        print(convert_broker_message_to_dict(message.body))
        await asyncio.sleep(1)
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
