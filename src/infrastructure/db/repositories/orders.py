from typing import Sequence

from sqlalchemy import RowMapping, func, select
from sqlalchemy.orm import joinedload, selectinload

from src.domain.orders import entities
from src.infrastructure.db.exceptions import UpdateException
from src.infrastructure.db.models.orders import Promotion
from src.infrastructure.db.models.schedules import Master, Schedule, Service, Slot, Order
from src.infrastructure.db.models.orders import UserPoint
from src.infrastructure.db.repositories.base import GenericSQLAlchemyRepository
from src.logic.dto.order_dto import PhotoDTO


class PromotionRepository(GenericSQLAlchemyRepository[Promotion, entities.Promotion]):
    model = Promotion

    async def add(self, entity: entities.Promotion) -> entities.Promotion:
        model = self.model.from_entity(entity)
        services = [Service.from_entity(service) for service in entity.services]
        model.services = [await self.session.merge(service) for service in services]
        self.session.add(model)
        await self.session.flush()
        return model.to_domain()

    async def update(self, entity: entities.Promotion) -> entities.Promotion:
        model = self.model.from_entity(entity)
        services = [Service.from_entity(service) for service in entity.services]
        model.services = [await self.session.merge(service) for service in services]
        await self.session.merge(model)
        await self.session.flush()
        return model.to_domain()

    async def find_all(self, **filter_by) -> list[entities.Promotion]:
        query = select(self.model).options(selectinload(self.model.services)).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [el.to_domain(with_join=True) for el in result.scalars().all()]

    async def find_one_or_none(self, **filter_by) -> entities.Promotion:
        query = select(self.model).options(selectinload(self.model.services)).filter_by(**filter_by)
        result = await self.session.execute(query)
        scalar = result.scalar_one_or_none()
        return scalar.to_domain(with_join=True) if scalar else None


class UserPointRepository(GenericSQLAlchemyRepository[UserPoint, entities.UserPoint]):
    model = UserPoint

    async def find_one_or_none(self, **filter_by) -> entities.UserPoint | None:
        query = select(self.model).options(joinedload(self.model.user)).filter_by(**filter_by)
        result = await self.session.execute(query)
        scalar = result.scalar_one_or_none()
        return scalar.to_domain(with_join=True) if scalar else None
