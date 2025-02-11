import asyncio
from collections import defaultdict

from datetime import date, timedelta
from typing import Type

from dishka import Provider, Scope, from_context, make_async_container, provide, AnyOf
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from src.presentation.api.settings import Settings, settings
from src.infrastructure.db.config import get_async_engine, get_async_session_factory, get_sync_engine


class DBProvider(Provider):
    scope = Scope.APP

    settings = from_context(provides=Settings)

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
