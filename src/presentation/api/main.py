from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from libcloud.storage.drivers.local import LocalStorageDriver
from sqladmin import Admin
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy_file.storage import StorageManager
from starlette.staticfiles import StaticFiles

from src.infrastructure.broker.rabbit.consumer import RabbitConsumer
from src.infrastructure.redis_adapter.redis_connector import RedisConnectorFactory
from src.logic.event_consumers.orders_consumers import UserCreatedEventConsumer
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

media_dir = Path("src/presentation/api/media")
photo_dir = media_dir / Path("photos")

photo_dir.mkdir(parents=True, exist_ok=True, mode=0o777)
container = LocalStorageDriver(str(media_dir)).get_container("photos")
StorageManager.add_storage("photos", container)


def create_fastapi_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(router_auth)
    app.include_router(router_users)
    app.include_router(schedule_router)
    app.include_router(order_router)
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


async def start_consumer(app: FastAPI):
    user_created_consumer = await app.state.dishka_container.get(UserCreatedEventConsumer)
    base_consumer = await app.state.dishka_container.get(RabbitConsumer)

    await base_consumer.consume_messages(
        user_created_consumer,
        queue_name=user_created_consumer.queue_name,
        exchange_name=user_created_consumer.exchange_name,
        routing_key=user_created_consumer.routing_key,
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    redis_connector = RedisConnectorFactory.create()
    redis_connection = await redis_connector.get_async_connection()
    FastAPICache.init(RedisBackend(redis_connection), prefix="cache")
    await add_sql_admin(app)
    await start_consumer(app)
    yield
    if redis_connection:
        await redis_connection.close()
    await app.state.dishka_container.close()


app = create_fastapi_app()
container = setup_container()
setup_dishka(container, app)
app.mount("/media", StaticFiles(directory=media_dir), name="media")
