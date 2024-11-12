from typing import Self

from src.infrastructure.db.repositories.users import UserPointRepository, UserRepository
from src.infrastructure.db.uow import SQLAlchemyAbstractUnitOfWork


class SQLAlchemyUsersUnitOfWork(SQLAlchemyAbstractUnitOfWork):
    async def __aenter__(self) -> Self:
        uow = await super().__aenter__()
        self.users = UserRepository(session=self._session)
        self.user_points = UserPointRepository(session=self._session)
        return uow
