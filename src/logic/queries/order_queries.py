from dataclasses import dataclass

from src.infrastructure.db.uows.order_uow import SQLAlchemyOrderQueryUnitOfWork
from src.logic.dto.order_dto import PromotionDetailDTO
from src.logic.queries.base import BaseQuery, QueryHandler


class GetAllPromotionsQuery(BaseQuery): ...


@dataclass(frozen=True)
class GetAllPromotionsQueryHandler(QueryHandler[GetAllPromotionsQuery, list[PromotionDetailDTO]]):
    uow: SQLAlchemyOrderQueryUnitOfWork

    async def handle(self, query: GetAllPromotionsQuery) -> list[PromotionDetailDTO]:
        async with self.uow:
            results = await self.uow.promotions.find_all()
        return results
