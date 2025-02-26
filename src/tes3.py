import asyncio

import orjson

from src.infrastructure.broker.rabbit.connector import RabbitConnector
from src.infrastructure.broker.rabbit.producer import Producer


async def get_service():
    async with RabbitConnector() as conn:
        pub = Producer(conn.channel)
        await pub.declare_exchange("user_create")
        await pub.publish_message(orjson.dumps({"a": 1}), "user_create", "user_create")
        # async


if __name__ == "__main__":
    asyncio.run(get_service())
    # asyncio.run(update())
