from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

# from libcloud.storage.drivers.local import LocalStorageDriver


# from sqlalchemy_file.storage import StorageManager
# from starlette.staticfiles import StaticFiles

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from sqladmin import Admin

from src.infrastructure.db.config import engine
from src.infrastructure.redis_adapter.redis_connector import RedisConnectorFactory
from src.presentation.api.admin.auth import authentication_backend
from src.presentation.api.admin.views import (
    UsersAdmin, InventoryAdmin,
    ScheduleAdmin, PromotionAdmin,  ConsumablesAdmin, MasterAdmin,
    SlotAdmin, UserPointAdmin, ServiceAdmin, OrderAdmin,
)

from src.presentation.api.users.router import router_auth, router_users
from src.presentation.api.schedules.router import router as schedule_router
from src.presentation.api.orders.router import router as order_router

# os.makedirs("app/media/photos", 0o777, exist_ok=True)
# container = LocalStorageDriver("app/media").get_container("photos")
# StorageManager.add_storage("default", container)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # os.makedirs("app/media/photos", 0o777, exist_ok=True)
    # os.makedirs("./media/photos", 0o777, exist_ok=True)
    # container = LocalStorageDriver("media").get_container("photos")
    # StorageManager.add_storage("default", container)

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

# app.mount('/app/media', StaticFiles(directory='app/media'), name='media')
# app.mount('/media', StaticFiles(directory='media'), name='media')

# os.makedirs("./upload_dir/attachment", 0o777, exist_ok=True)
# container = LocalStorageDriver("./upload_dir").get_container("attachment")
# StorageManager.add_storage("default", container)


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
