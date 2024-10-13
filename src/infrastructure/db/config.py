from asyncio import current_task

from sqlalchemy import NullPool, create_engine
from sqlalchemy.ext.asyncio import async_scoped_session, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.presentation.api.settings import settings

if settings.MODE == "TEST":
    DATABASE_URL = settings.TEST_DATABASE_URL
    DATABASE_URL_SYNC = settings.TEST_DATABASE_URL_SYNC
    DATABASE_PARAMS = {
        "poolclass": NullPool,
        "future": True,
        "echo": True,
        "pool_pre_ping": True,
    }
else:
    DATABASE_URL = settings.DATABASE_URL
    DATABASE_URL_SYNC = settings.DATABASE_URL_SYNC
    DATABASE_PARAMS = {"future": True, "echo": True, "pool_pre_ping": True, "pool_size": 50, "max_overflow": 15}


engine = create_async_engine(DATABASE_URL, **DATABASE_PARAMS)

AsyncSessionFactory = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)


AsyncScopedSession = async_scoped_session(session_factory=AsyncSessionFactory, scopefunc=current_task)

sync_engine = create_engine(url=DATABASE_URL_SYNC, **DATABASE_PARAMS)

SyncSessionFactory = sessionmaker(sync_engine, autoflush=False, expire_on_commit=False)
