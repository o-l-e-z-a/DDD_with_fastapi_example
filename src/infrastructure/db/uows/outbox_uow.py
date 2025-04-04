from typing import Self

from src.infrastructure.db.repositories.outbox import OutboxMessageRepository
from src.infrastructure.db.uows.base import SQLAlchemyAbstractUnitOfWork


class SQLAlchemyOutboxUnitOfWork(SQLAlchemyAbstractUnitOfWork):
    async def __aenter__(self) -> Self:
        uow = await super().__aenter__()
        self.outbox = OutboxMessageRepository(session=self._session)
        return uow
