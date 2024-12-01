from typing import Self

from src.infrastructure.db.repositories.orders import OrderRepository, PromotionRepository
from src.infrastructure.db.repositories.schedules import (
    ConsumablesRepository,
    InventoryRepository,
    ScheduleRepository,
    ServiceRepository,
    SlotRepository,
)
from src.infrastructure.db.repositories.users import UserPointRepository, UserRepository
from src.infrastructure.db.uow import SQLAlchemyAbstractUnitOfWork


class SQLAlchemyOrderUnitOfWork(SQLAlchemyAbstractUnitOfWork):
    async def __aenter__(self) -> Self:
        uow = await super().__aenter__()
        self.schedules = ScheduleRepository(session=self._session)
        self.slots = SlotRepository(session=self._session)
        self.consumables = ConsumablesRepository(session=self._session)
        self.inventories = InventoryRepository(session=self._session)
        self.services = ServiceRepository(session=self._session)
        self.users = UserRepository(session=self._session)
        self.promotions = PromotionRepository(session=self._session)
        self.orders = OrderRepository(session=self._session)
        self.user_points = UserPointRepository(session=self._session)
        return uow
