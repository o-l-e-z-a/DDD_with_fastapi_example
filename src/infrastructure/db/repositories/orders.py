from typing import Sequence

from sqlalchemy import RowMapping, func, select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy_file import File
from sqlalchemy_file.exceptions import ContentTypeValidationError

from src.domain.orders import entities
from src.infrastructure.db.exceptions import UpdateException
from src.infrastructure.db.models.orders import Order, Promotion
from src.infrastructure.db.models.schedules import Master, Schedule, Service, Slot
from src.infrastructure.db.repositories.base import GenericSQLAlchemyRepository
from src.logic.dto.order_dto import PhotoDTO


class OrderRepository(GenericSQLAlchemyRepository[Order, entities.Order]):
    model = Order

    async def get_order_report_by_service(self) -> Sequence[RowMapping]:
        query = (
            select(
                Service.id,
                Service.name,
                Service.price,
                func.count(Service.id).label("total_count"),
                func.sum(Order.total_amount).label("total_sum"),
            )
            .join(Schedule)
            .join(Slot)
            .join(Order)
            .group_by(Service.id)
        )
        result = await self.session.execute(query)
        return result.mappings().all()

    async def find_one_or_none(self, **filter_by) -> entities.Order | None:
        query = self.get_query_to_find_all(**filter_by)
        result = await self.session.execute(query)
        scalar = result.scalar_one_or_none()
        return scalar.to_domain(with_join=True, child_level=4) if scalar else None

    async def find_all(self, **filter_by) -> list[entities.Order]:
        query = self.get_query_to_find_all(**filter_by)
        result = await self.session.execute(query)
        return [el.to_domain(with_join=True, child_level=4) for el in result.scalars().all()]

    # def find_order_by_day(self, day):
    #     user_2 = aliased(Users)
    #     user_1 = aliased(Users)
    #     query = (
    #         select(Order)
    #         .join(Slot).join(Schedule).join(Service).join(Master)
    #         .join(user_1, Master.user_id == user_1.id)
    #         .join(user_2, Order.user_id == user_2.id)
    #         .options(
    #             contains_eager(Order.slot)
    #             .contains_eager(Slot.schedule)
    #             .options(contains_eager(Schedule.service))
    #             .options(contains_eager(Schedule.master).contains_eager(Master.user.of_type(user_1)))
    #         )
    #         .options(contains_eager(Order.user.of_type(user_2)))
    #         .where(Schedule.day == day)
    #     )
    #     result = self.session.execute(query)
    #     return result.scalars().all()

    def get_query_to_find_all(self, **filter_by):
        query = (
            select(self.model)
            .options(
                joinedload(self.model.slot, innerjoin=True)
                .joinedload(Slot.schedule, innerjoin=True)
                .options(joinedload(Schedule.service, innerjoin=True).options(selectinload(Service.consumables)))
                .options(
                    joinedload(Schedule.master, innerjoin=True)
                    .options(joinedload(Master.user, innerjoin=True))
                    .options(selectinload(Master.services))
                )
            )
            .options(joinedload(self.model.user, innerjoin=True))
            .filter_by(**filter_by)
        )
        return query

    async def update_photo(self, entity: entities.Order, photo_after: PhotoDTO, photo_before: PhotoDTO):
        model = self.model.from_entity(entity)
        model.photo_before = File(  # type: ignore[assignment]
            content=photo_before, content_type=photo_before.content_type, filename=photo_before.filename
        )
        model.photo_after = File(  # type: ignore[assignment]
            content=photo_after, content_type=photo_after.content_type, filename=photo_after.filename
        )
        try:
            await self.session.merge(model)
            await self.session.flush()
        except ContentTypeValidationError as err:
            # print(err.msg)
            raise UpdateException(detail=err.msg, entity=entity)
        return model.to_domain()


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
