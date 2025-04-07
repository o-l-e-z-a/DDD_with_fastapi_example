import asyncio

from src.infrastructure.logger_adapter.logger import init_logger
from src.infrastructure.tkq.broker import taskiq_broker

logger = init_logger(__name__)


@taskiq_broker.task
async def add_one(value: int) -> int:
    logger.debug(f"value: {value}")
    await asyncio.sleep(10)
    value += 1
    logger.debug(f"value: {value}")
    return value


# @taskiq_broker.task
# async def add_two():
#     print("in add_two")
#     order_canceled_consumer = await container.get(OrderCancelledEventConsumer)
#     base_consumer = await container.get(RabbitConsumer)
#     consumer = order_canceled_consumer
#     print(f"start consume_messages")
#     await base_consumer.consume_messages(
#         consumer,
#         queue_name=consumer.queue_name,
#         exchange_name=consumer.exchange_name,
#         routing_key=consumer.routing_key,
#     )
#     print(f'finished consume_messages')
#
#
# container = setup_container()
