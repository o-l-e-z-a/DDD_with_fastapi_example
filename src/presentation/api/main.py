from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from libcloud.storage.drivers.local import LocalStorageDriver
from sqladmin import Admin
from sqlalchemy_file.storage import StorageManager
from starlette.staticfiles import StaticFiles

from src.infrastructure.db.config import engine
from src.infrastructure.redis_adapter.redis_connector import RedisConnectorFactory
from src.presentation.api.admin.auth import authentication_backend
from src.presentation.api.admin.views import (
    ConsumablesAdmin,
    InventoryAdmin,
    MasterAdmin,
    OrderAdmin,
    PromotionAdmin,
    ScheduleAdmin,
    ServiceAdmin,
    SlotAdmin,
    UserPointAdmin,
    UsersAdmin,
)
from src.presentation.api.orders.router import router as order_router
from src.presentation.api.schedules.router import router as schedule_router
from src.presentation.api.users.router import router_auth, router_users

media_dir = Path("src/presentation/api/media")
photo_dir = media_dir / Path("photos")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    photo_dir.mkdir(parents=True, exist_ok=True, mode=0o777)
    container = LocalStorageDriver(str(media_dir)).get_container("photos")
    StorageManager.add_storage("photos", container)

    redis_connector = RedisConnectorFactory.create()
    redis_connection = await redis_connector.get_async_connection()
    FastAPICache.init(RedisBackend(redis_connection), prefix="cache")
    yield
    if redis_connection:
        await redis_connection.close()


app = FastAPI(lifespan=lifespan)

app.include_router(router_auth)
app.include_router(router_users)
app.include_router(schedule_router)
app.include_router(order_router)

app.mount("/media", StaticFiles(directory=media_dir), name="media")

admin = Admin(app, engine, authentication_backend=authentication_backend)
admin.add_view(UsersAdmin)
admin.add_view(InventoryAdmin)
admin.add_view(ScheduleAdmin)
admin.add_view(ServiceAdmin)
admin.add_view(PromotionAdmin)
admin.add_view(ConsumablesAdmin)
admin.add_view(MasterAdmin)
admin.add_view(SlotAdmin)
admin.add_view(UserPointAdmin)
admin.add_view(OrderAdmin)
