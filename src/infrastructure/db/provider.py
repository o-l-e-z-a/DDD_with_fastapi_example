from dishka import Provider, Scope, from_context, provide
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from src.infrastructure.db.config import get_async_engine, get_async_session_factory, get_sync_engine
from src.infrastructure.db.uows.order_uow import SQLAlchemyOrderQueryUnitOfWork, SQLAlchemyOrderUnitOfWork
from src.infrastructure.db.uows.schedule_uow import SQLAlchemyScheduleQueryUnitOfWork, SQLAlchemyScheduleUnitOfWork
from src.infrastructure.db.uows.users_uow import SQLAlchemyUsersQueryUnitOfWork, SQLAlchemyUsersUnitOfWork
from src.presentation.api.settings import Settings


class DBProvider(Provider):
    scope = Scope.APP
    settings = from_context(provides=Settings, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def engine(self, setting: Settings) -> AsyncEngine:
        engine = get_async_engine(setting)
        return engine

    @provide(scope=Scope.APP)
    def sync_engine(self, setting: Settings) -> Engine:
        engine = get_sync_engine(setting)
        return engine

    @provide(scope=Scope.APP)
    def get_async_session_maker(self, engine: AsyncEngine) -> async_sessionmaker:
        return get_async_session_factory(engine)

    user_uow = provide(SQLAlchemyUsersUnitOfWork)
    schedule_uow = provide(SQLAlchemyScheduleUnitOfWork)
    order_uow = provide(SQLAlchemyOrderUnitOfWork)

    user_query_uow = provide(SQLAlchemyUsersQueryUnitOfWork)
    schedule_query_uow = provide(SQLAlchemyScheduleQueryUnitOfWork)
    order_query_uow = provide(SQLAlchemyOrderQueryUnitOfWork)
