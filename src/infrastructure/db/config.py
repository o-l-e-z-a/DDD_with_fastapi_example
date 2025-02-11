from sqlalchemy import NullPool, create_engine, Engine
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from src.presentation.api.settings import Settings


def get_db_params(settings: Settings):
    if settings.MODE == "TEST":
        DATABASE_URL = settings.db.TEST_DATABASE_URL
        DATABASE_URL_SYNC = settings.db.TEST_DATABASE_URL_SYNC
        DATABASE_PARAMS = {
            "poolclass": NullPool,
            "future": True,
            "echo": False,
            "pool_pre_ping": True,
        }
    else:
        DATABASE_URL = settings.db.DATABASE_URL
        DATABASE_URL_SYNC = settings.db.DATABASE_URL_SYNC
        DATABASE_PARAMS = {"future": True, "echo": True, "pool_pre_ping": True, "pool_size": 50, "max_overflow": 15}
    return DATABASE_URL, DATABASE_URL_SYNC, DATABASE_PARAMS


def get_async_engine(settings: Settings) -> AsyncEngine:
    DATABASE_URL, DATABASE_URL_SYNC, DATABASE_PARAMS = get_db_params(settings)
    engine = create_async_engine(DATABASE_URL, **DATABASE_PARAMS)
    return engine


def get_sync_engine(settings: Settings) -> Engine:
    DATABASE_URL, DATABASE_URL_SYNC, DATABASE_PARAMS = get_db_params(settings)
    engine = create_engine(url=DATABASE_URL_SYNC, **DATABASE_PARAMS)
    return engine


def get_async_session_factory(engine: AsyncEngine) -> async_sessionmaker:
    AsyncSessionFactory = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)
    return AsyncSessionFactory


# AsyncScopedSession = async_scoped_session(session_factory=AsyncSessionFactory, scopefunc=current_task)
# SyncSessionFactory = sessionmaker(sync_engine, autoflush=False, expire_on_commit=False)
