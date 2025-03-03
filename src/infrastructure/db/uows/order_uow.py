from typing import Self

from src.infrastructure.db.repositories.orders import (
    OrderPaymentQueryRepository,
    OrderPaymentRepository,
    PromotionQueryRepository,
    PromotionRepository,
    UserPointQueryRepository,
    UserPointRepository,
)
from src.infrastructure.db.repositories.schedules import OrderRepository, ServiceRepository
from src.infrastructure.db.repositories.users import UserRepository
from src.infrastructure.db.uows.base import SQLAlchemyAbstractUnitOfWork


class SQLAlchemyOrderUnitOfWork(SQLAlchemyAbstractUnitOfWork):
    async def __aenter__(self) -> Self:
        uow = await super().__aenter__()
        self.services = ServiceRepository(session=self._session)
        self.users = UserRepository(session=self._session)
        self.promotions = PromotionRepository(session=self._session)
        self.orders = OrderRepository(session=self._session)
        self.order_payments = OrderPaymentRepository(session=self._session)
        self.user_points = UserPointRepository(session=self._session)
        return uow


class SQLAlchemyOrderQueryUnitOfWork(SQLAlchemyAbstractUnitOfWork):
    async def __aenter__(self) -> Self:
        uow = await super().__aenter__()
        self.promotions = PromotionQueryRepository(session=self._session)
        self.user_points = UserPointQueryRepository(session=self._session)
        self.order_payments = OrderPaymentQueryRepository(session=self._session)
        return uow
