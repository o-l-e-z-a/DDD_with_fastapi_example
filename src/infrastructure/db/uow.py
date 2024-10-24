from __future__ import annotations

import abc

from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.infrastructure.db.config import AsyncSessionFactory


class AbstractUnitOfWork(abc.ABC):
    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args, **kwargs) -> None:
        await self.rollback()

    @abc.abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError


class SQLAlchemyAbstractUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory: async_sessionmaker = AsyncSessionFactory) -> None:
        super().__init__()
        self._session_factory: async_sessionmaker = session_factory

    async def __aenter__(self) -> Self:
        self._session: AsyncSession = self._session_factory()
        return await super().__aenter__()

    async def __aexit__(self, *args, **kwargs) -> None:
        await super().__aexit__(*args, **kwargs)
        await self._session.close()

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        self._session.expunge_all()
        await self._session.rollback()
