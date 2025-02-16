from typing import Self

from src.infrastructure.db.repositories.users import UserQueryRepository, UserRepository
from src.infrastructure.db.uows.base import SQLAlchemyAbstractUnitOfWork


class SQLAlchemyUsersUnitOfWork(SQLAlchemyAbstractUnitOfWork):
    async def __aenter__(self) -> Self:
        uow = await super().__aenter__()
        self.users = UserRepository(session=self._session)
        return uow


class SQLAlchemyUsersQueryUnitOfWork(SQLAlchemyAbstractUnitOfWork):
    async def __aenter__(self) -> Self:
        uow = await super().__aenter__()
        self.users = UserQueryRepository(session=self._session)
        return uow
