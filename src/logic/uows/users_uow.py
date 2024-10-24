from typing import Self

from src.infrastructure.db.repositories.users import UserPointRepository, UserRepository
from src.infrastructure.db.uow import SQLAlchemyAbstractUnitOfWork


class SQLAlchemyUsersUnitOfWork(SQLAlchemyAbstractUnitOfWork):
    user: UserRepository
    user_point: UserPointRepository

    async def __aenter__(self) -> Self:
        uow = await super().__aenter__()
        self.users: UserRepository = UserRepository(session=self._session)
        self.users_statistics: UserPointRepository = UserPointRepository(session=self._session)
        return uow
