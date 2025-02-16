from typing import Self

from src.infrastructure.db.repositories.schedules import (
    MasterQueryRepository,
    MasterRepository,
    OrderQueryRepository,
    OrderRepository,
    ScheduleQueryRepository,
    ScheduleRepository,
    ServiceQueryRepository,
    ServiceRepository,
)
from src.infrastructure.db.repositories.users import UserQueryRepository, UserRepository
from src.infrastructure.db.uows.base import SQLAlchemyAbstractUnitOfWork


class SQLAlchemyScheduleUnitOfWork(SQLAlchemyAbstractUnitOfWork):
    async def __aenter__(self) -> Self:
        uow = await super().__aenter__()
        self.masters = MasterRepository(session=self._session)
        self.schedules = ScheduleRepository(session=self._session)
        self.services = ServiceRepository(session=self._session)
        self.orders = OrderRepository(session=self._session)
        self.users = UserRepository(session=self._session)
        return uow


class SQLAlchemyScheduleQueryUnitOfWork(SQLAlchemyAbstractUnitOfWork):
    async def __aenter__(self) -> Self:
        uow = await super().__aenter__()
        self.masters = MasterQueryRepository(session=self._session)
        self.schedules = ScheduleQueryRepository(session=self._session)
        self.services = ServiceQueryRepository(session=self._session)
        self.orders = OrderQueryRepository(session=self._session)
        self.users = UserQueryRepository(session=self._session)
        return uow
