from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload

from src.domain.orders import entities
from src.infrastructure.db.exceptions import InsertException
from src.infrastructure.db.models.orders import OrderPayment, Promotion, PromotionToService, UserPoint
from src.infrastructure.db.repositories.base import GenericSQLAlchemyQueryRepository, GenericSQLAlchemyRepository
from src.logic.dto.mappers.order_mappers import (
    order_payment_detail_dto_mapper,
    promotion_to_detail_dto_mapper,
    user_point_dto_mapper,
)
from src.logic.dto.order_dto import OrderPaymentDetailDTO, PromotionDetailDTO, UserPointDTO


class PromotionRepository(GenericSQLAlchemyRepository[Promotion, entities.Promotion]):
    model = Promotion

    async def add(self, entity: entities.Promotion) -> entities.Promotion:
        model = self.model.from_entity(entity)
        services = [PromotionToService(service_id=service_id) for service_id in entity.services_id]
        model.services = services
        self.session.add(model)
        try:
            await self.session.flush()
        except IntegrityError as err:
            raise InsertException(entity=entity, detail=str(err.args))
        return model.to_domain()

    async def update(self, entity: entities.Promotion) -> entities.Promotion:
        model = self.model.from_entity(entity)
        services = [
            PromotionToService(service_id=service_id, promotion_id=entity.id) for service_id in entity.services_id
        ]
        model.services = services
        await self.session.merge(model)
        try:
            await self.session.flush()
        except IntegrityError as err:
            raise InsertException(entity=entity, detail=str(err.args))
        return model.to_domain()

    async def find_one_or_none(self, **filter_by) -> entities.Promotion:
        query = select(self.model).options(selectinload(self.model.services)).filter_by(**filter_by)
        result = await self.session.execute(query)
        scalar = result.scalar_one_or_none()
        return scalar.to_domain() if scalar else None


class UserPointRepository(GenericSQLAlchemyRepository[UserPoint, entities.UserPoint]):
    model = UserPoint

    async def find_one_or_none(self, **filter_by) -> entities.UserPoint | None:
        query = select(self.model).options(joinedload(self.model.user)).filter_by(**filter_by)
        result = await self.session.execute(query)
        scalar = result.scalar_one_or_none()
        return scalar.to_domain() if scalar else None


class OrderPaymentRepository(GenericSQLAlchemyRepository[OrderPayment, entities.OrderPayment]):
    model = OrderPayment


class PromotionQueryRepository(GenericSQLAlchemyQueryRepository[Promotion]):
    async def find_all(self, **filter_by) -> list[PromotionDetailDTO]:
        query = select(Promotion).options(selectinload(Promotion.services)).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [promotion_to_detail_dto_mapper(el) for el in result.scalars().all()]


class UserPointQueryRepository(GenericSQLAlchemyQueryRepository[UserPoint]):
    async def find_one_or_none(self, **filter_by) -> UserPointDTO | None:
        query = select(UserPoint).filter_by(**filter_by)
        result = await self.session.execute(query)
        scalar = result.scalar_one_or_none()
        return user_point_dto_mapper(scalar) if scalar else None


class OrderPaymentQueryRepository(GenericSQLAlchemyQueryRepository[OrderPayment]):
    async def find_one_or_none(self, **filter_by) -> OrderPaymentDetailDTO | None:
        query = select(OrderPayment).filter_by(**filter_by)
        result = await self.session.execute(query)
        scalar = result.scalar_one_or_none()
        return order_payment_detail_dto_mapper(scalar) if scalar else None
