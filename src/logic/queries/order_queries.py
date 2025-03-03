from dataclasses import dataclass

from pydantic import PositiveInt

from src.infrastructure.db.uows.order_uow import SQLAlchemyOrderQueryUnitOfWork
from src.logic.dto.order_dto import OrderPaymentDetailDTO, PromotionDetailDTO, UserPointDTO
from src.logic.queries.base import BaseQuery, QueryHandler


class GetAllPromotionsQuery(BaseQuery): ...


class UserPointQuery(BaseQuery):
    user_id: PositiveInt


class OrderPaymentDetailQuery(BaseQuery):
    order_payment_id: PositiveInt


@dataclass(frozen=True)
class GetAllPromotionsQueryHandler(QueryHandler[GetAllPromotionsQuery, list[PromotionDetailDTO]]):
    uow: SQLAlchemyOrderQueryUnitOfWork

    async def handle(self, query: GetAllPromotionsQuery) -> list[PromotionDetailDTO]:
        async with self.uow:
            results = await self.uow.promotions.find_all()
        return results


@dataclass(frozen=True)
class UserPointQueryHandler(QueryHandler[UserPointQuery, UserPointDTO | None]):
    uow: SQLAlchemyOrderQueryUnitOfWork

    async def handle(self, query: UserPointQuery) -> UserPointDTO | None:
        async with self.uow:
            results = await self.uow.user_points.find_one_or_none(user_id=query.user_id)
        return results


@dataclass(frozen=True)
class OrderPaymentDetailQueryHandler(QueryHandler[OrderPaymentDetailQuery, list[PromotionDetailDTO]]):
    uow: SQLAlchemyOrderQueryUnitOfWork

    async def handle(self, query: OrderPaymentDetailQuery) -> OrderPaymentDetailDTO | None:
        async with self.uow:
            results = await self.uow.order_payments.find_one_or_none(id=query.order_payment_id)
        return results
