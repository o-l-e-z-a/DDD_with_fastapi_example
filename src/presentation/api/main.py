import asyncio

from contextlib import asynccontextmanager
from typing import AsyncIterator

from dishka import AsyncContainer
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from sqladmin import Admin
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.staticfiles import StaticFiles

from src.infrastructure.broker.rabbit.consumer import RabbitConsumer
from src.infrastructure.db.utils import media_dir
from src.infrastructure.redis_adapter.redis_connector import RedisConnectorFactory
from src.infrastructure.tkq.broker import taskiq_broker
from src.logic.event_consumers.orders_consumers import (
    OrderCancelledEventConsumer,
    OrderCreatedEventConsumer,
    OrderPayedEventConsumer,
    OrderPaymentCancelledEventConsumer,
    UserCreatedEventConsumer,
)
from src.presentation.api.admin.auth import authentication_backend
from src.presentation.api.admin.views import (
    MasterAdmin,
    OrderAdmin,
    PromotionAdmin,
    ScheduleAdmin,
    ServiceAdmin,
    SlotAdmin,
    UserPointAdmin,
    UsersAdmin,
)
from src.presentation.api.dependencies import setup_container
from src.presentation.api.orders.router import router as order_router
from src.presentation.api.schedules.router import router as schedule_router
from src.presentation.api.users.router import router_auth, router_users


def create_fastapi_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(router_auth)
    app.include_router(router_users)
    app.include_router(schedule_router)
    app.include_router(order_router)
    setup_dishka(container, app)
    return app


async def add_sql_admin(app: FastAPI):
    async_engine = await app.state.dishka_container.get(AsyncEngine)
    admin = Admin(app, async_engine, authentication_backend=authentication_backend)
    admin.add_view(UsersAdmin)
    admin.add_view(ScheduleAdmin)
    admin.add_view(ServiceAdmin)
    admin.add_view(PromotionAdmin)
    admin.add_view(MasterAdmin)
    admin.add_view(SlotAdmin)
    admin.add_view(UserPointAdmin)
    admin.add_view(OrderAdmin)


async def start_consumer(container: AsyncContainer):
    user_created_consumer = await container.get(UserCreatedEventConsumer)
    order_created_consumer = await container.get(OrderCreatedEventConsumer)
    order_payed_consumer = await container.get(OrderPayedEventConsumer)
    order_payment_canceled_consumer = await container.get(OrderPaymentCancelledEventConsumer)
    order_canceled_consumer = await container.get(OrderCancelledEventConsumer)
    base_consumer: RabbitConsumer = await container.get(RabbitConsumer)

    consumers = [
        user_created_consumer,
        order_created_consumer,
        order_payed_consumer,
        order_payment_canceled_consumer,
        order_canceled_consumer,
    ]
    tasks = []
    for consumer in consumers:
        # create task in loop
        coro = asyncio.create_task(
            base_consumer.consume_messages(
                consumer,
                queue_name=consumer.queue_name,
                exchange_name=consumer.exchange_name,
                routing_key=consumer.routing_key,
            )
        )
        tasks.append(coro)
    return tasks


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    redis_connector = RedisConnectorFactory.create()
    redis_connection = await redis_connector.get_async_connection()
    FastAPICache.init(RedisBackend(redis_connection), prefix="cache")
    await add_sql_admin(app)

    consumer_tasks = await start_consumer(app.state.dishka_container)
    app.state.consumer_tasks = consumer_tasks

    if not taskiq_broker.is_worker_process:
        await taskiq_broker.startup()

    yield

    if not taskiq_broker.is_worker_process:
        await taskiq_broker.shutdown()

    for task in app.state.consumer_tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    if redis_connection:
        await redis_connection.close()

    await app.state.dishka_container.close()


container = setup_container()
app = create_fastapi_app()
app.mount("/media", StaticFiles(directory=media_dir), name="media")
