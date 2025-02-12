from typing import Self

from src.infrastructure.db.repositories.schedules import (
    MasterRepository,
    ScheduleRepository,
    ServiceRepository,
    OrderRepository,
)
from src.infrastructure.db.repositories.users import UserRepository
from src.infrastructure.db.uow import SQLAlchemyAbstractUnitOfWork


class SQLAlchemyScheduleUnitOfWork(SQLAlchemyAbstractUnitOfWork):
    async def __aenter__(self) -> Self:
        uow = await super().__aenter__()
        self.masters = MasterRepository(session=self._session)
        self.schedules = ScheduleRepository(session=self._session)
        self.services = ServiceRepository(session=self._session)
        self.orders = OrderRepository(session=self._session)
        self.users = UserRepository(session=self._session)
        return uow
