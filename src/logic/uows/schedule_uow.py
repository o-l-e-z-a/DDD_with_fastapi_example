from typing import Self

from src.infrastructure.db.repositories.schedules import (
    ConsumablesRepository,
    InventoryRepository,
    MasterRepository,
    ScheduleRepository,
    ServiceRepository,
    SlotRepository,
)
from src.infrastructure.db.repositories.users import UserRepository
from src.infrastructure.db.uow import SQLAlchemyAbstractUnitOfWork


class SQLAlchemyScheduleUnitOfWork(SQLAlchemyAbstractUnitOfWork):
    async def __aenter__(self) -> Self:
        uow = await super().__aenter__()
        self.schedules = ScheduleRepository(session=self._session)
        self.slots = SlotRepository(session=self._session)
        self.consumables = ConsumablesRepository(session=self._session)
        self.masters = MasterRepository(session=self._session)
        self.services = ServiceRepository(session=self._session)
        self.inventories = InventoryRepository(session=self._session)
        self.users = UserRepository(session=self._session)
        return uow
