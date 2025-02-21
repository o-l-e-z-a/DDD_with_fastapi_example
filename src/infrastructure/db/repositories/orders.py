from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload

from src.domain.orders import entities
from src.infrastructure.db.exceptions import InsertException
from src.infrastructure.db.models.orders import Promotion, UserPoint
from src.infrastructure.db.models.schedules import Service
from src.infrastructure.db.repositories.base import GenericSQLAlchemyQueryRepository, GenericSQLAlchemyRepository
from src.logic.dto.mappers import promotion_to_detail_dto_mapper
from src.logic.dto.order_dto import PromotionDetailDTO


class PromotionRepository(GenericSQLAlchemyRepository[Promotion, entities.Promotion]):
    model = Promotion

    async def add(self, entity: entities.Promotion) -> entities.Promotion:
        model = self.model.from_entity(entity)
        services = [await self.session.get(Service, service_id) for service_id in entity.services_id]
        model.services = [await self.session.merge(service) for service in services]
        self.session.add(model)
        try:
            await self.session.flush()
        except IntegrityError as err:
            raise InsertException(entity=entity, detail=str(err.args))
        return model.to_domain()

    async def update(self, entity: entities.Promotion) -> entities.Promotion:
        model = self.model.from_entity(entity)
        services = [await self.session.get(Service, service_id) for service_id in entity.services_id]
        model.services = [await self.session.merge(service) for service in services]
        await self.session.merge(model)
        try:
            await self.session.flush()
        except IntegrityError as err:
            raise InsertException(entity=entity, detail=str(err.args))
        return model.to_domain()

    async def find_all(self, **filter_by) -> list[entities.Promotion]:
        query = select(self.model).options(selectinload(self.model.services)).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [el.to_domain() for el in result.scalars().all()]

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
        return scalar.to_domain(with_join=True) if scalar else None


class PromotionQueryRepository(GenericSQLAlchemyQueryRepository[Promotion]):
    async def find_all(self, **filter_by) -> list[PromotionDetailDTO]:
        query = select(Promotion).options(selectinload(Promotion.services)).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [promotion_to_detail_dto_mapper(el) for el in result.scalars().all()]


# class UserPointQueryRepository(GenericSQLAlchemyRepository[UserPoint, entities.UserPoint]):
#     model = UserPoint
#
#     async def find_one_or_none(self, **filter_by) -> entities.UserPoint | None:
#         query = select(UserPoint).options(joinedload(UserPoint.user)).filter_by(**filter_by)
#         result = await self.session.execute(query)
#         scalar = result.scalar_one_or_none()
#         return scalar.to_domain(with_join=True) if scalar else None
