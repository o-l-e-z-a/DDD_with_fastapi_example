from fastapi import FastAPI

# from libcloud.storage.drivers.local import LocalStorageDriver


# from sqlalchemy_file.storage import StorageManager
# from starlette.staticfiles import StaticFiles

# from app.infrastructure.redis_config import get_redis_connection
# from app.admin.auth import authentication_backend
# from app.admin.views import (
#     UsersAdmin, InventoryAdmin,
#     ScheduleAdmin, PromotionAdmin,  ConsumablesAdmin, MasterAdmin,
#     SlotAdmin, UserPointAdmin, ServiceAdmin, OrderAdmin,
# )
#
# from app.procedure.router import router as procedure_router
# from app.schedule.router import router as schedule_router
# from app.promotion.router import router as promotion_router
# from app.order.router import router as order_router
# from app.users.router import router_auth, router_users

# os.makedirs("app/media/photos", 0o777, exist_ok=True)
# container = LocalStorageDriver("app/media").get_container("photos")
# StorageManager.add_storage("default", container)


# @asynccontextmanager
# async def lifespan(_: FastAPI) -> AsyncIterator[None]:
# os.makedirs("app/media/photos", 0o777, exist_ok=True)
# os.makedirs("./media/photos", 0o777, exist_ok=True)
# container = LocalStorageDriver("media").get_container("photos")
# StorageManager.add_storage("default", container)

# redis_connection = get_redis_connection(decode_responses=False)
# FastAPICache.init(RedisBackend(redis_connection), prefix="cache")
# yield
#
# await redis_connection.close()

# app = FastAPI(lifespan=lifespan)
app = FastAPI()

# app.include_router(router_auth)
# app.include_router(router_users)
# app.include_router(procedure_router)
# app.include_router(schedule_router)
# app.include_router(promotion_router)
# app.include_router(order_router)

# app.mount('/app/media', StaticFiles(directory='app/media'), name='media')
# app.mount('/media', StaticFiles(directory='media'), name='media')

# os.makedirs("./upload_dir/attachment", 0o777, exist_ok=True)
# container = LocalStorageDriver("./upload_dir").get_container("attachment")
# StorageManager.add_storage("default", container)


# admin = Admin(
#     app, engine,
#     authentication_backend=authentication_backend
# )
# admin.add_view(UsersAdmin)
# admin.add_view(InventoryAdmin)
# admin.add_view(ScheduleAdmin)
# admin.add_view(ServiceAdmin)
# admin.add_view(PromotionAdmin)
# admin.add_view(ConsumablesAdmin)
# admin.add_view(MasterAdmin)
# admin.add_view(SlotAdmin)
# admin.add_view(UserPointAdmin)
# admin.add_view(OrderAdmin)
