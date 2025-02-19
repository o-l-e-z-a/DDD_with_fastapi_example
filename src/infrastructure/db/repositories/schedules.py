from datetime import date
from typing import Sequence

from sqlalchemy import RowMapping, and_, extract, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import contains_eager, joinedload, selectinload
from sqlalchemy_file import File
from sqlalchemy_file.exceptions import ContentTypeValidationError

from src.domain.schedules import entities
from src.domain.schedules.entities import OrderStatus
from src.domain.users import entities as user_entities
from src.infrastructure.db.exceptions import InsertException, UpdateException
from src.infrastructure.db.models.schedules import Master, Order, Schedule, Service, Slot
from src.infrastructure.db.models.users import Users
from src.infrastructure.db.repositories.base import GenericSQLAlchemyQueryRepository, GenericSQLAlchemyRepository
from src.logic.dto.mappers import user_to_detail_dto_mapper, service_to_detail_dto_mapper, master_to_detail_dto_mapper, \
    schedule_to_detail_dto_mapper, order_to_detail_dto_mapper
from src.logic.dto.schedule_dto import MasterDetailDTO, ServiceDTO, ScheduleDetailDTO, OrderDetailDTO
from src.logic.dto.user_dto import UserDetailDTO


class ServiceRepository(GenericSQLAlchemyRepository[Service, entities.Service]):
    model = Service

    async def get_services_by_ids(self, ids: list[int]) -> list[entities.Service]:
        query = select(self.model).where(self.model.id.in_(ids))
        result = await self.session.execute(query)
        return [el.to_domain() for el in result.scalars().all()]


class MasterRepository(GenericSQLAlchemyRepository[Master, entities.Master]):
    model = Master

    async def add(self, entity: entities.Master) -> entities.Master:
        model = self.model.from_entity(entity)
        services = [await self.session.get(Service, service_id) for service_id in entity.services_id]
        model.services = services
        self.session.add(model)
        try:
            await self.session.flush()
        except IntegrityError as err:
            raise InsertException(entity=entity, detail=str(err.args))
        return model.to_domain(with_join=True)

    async def get_users_to_masters(self) -> list[user_entities.User]:
        query = select(Users).where(~Users.master.has())
        result = await self.session.execute(query)
        return [el.to_domain() for el in result.scalars().all()]

    async def find_all(self, **filter_by) -> list[entities.Master]:
        query = (
            select(self.model)
            .options(joinedload(self.model.user))
            .options(selectinload(self.model.services))
            .filter_by(**filter_by)
        )
        result = await self.session.execute(query)
        return [el.to_domain(with_join=True) for el in result.scalars().all()]

    async def find_one_or_none(self, **filter_by) -> entities.Master | None:
        query = (
            select(self.model)
            .options(joinedload(self.model.user))
            .options(selectinload(self.model.services))
            .filter_by(**filter_by)
        )
        result = await self.session.execute(query)
        scalar = result.scalar_one_or_none()
        return scalar.to_domain(with_join=True) if scalar else None

    async def filter_by_service(self, service_id: int) -> list[entities.Master]:
        query = (
            select(self.model)
            .options(joinedload(self.model.user))
            .options(selectinload(self.model.services))
            .where(Service.id == service_id)
        )
        result = await self.session.execute(query)
        return [el.to_domain(with_join=True) for el in result.scalars().all()]

    async def get_order_report_by_master(self, month: int | None = None):
        month = month if month else date.today().month
        master_with_reports = (
            select(
                Master.id,
                Master.user_id,
                func.count(Master.id).label("total_count"),
                # func.sum(Order.total_amount).label("total_sum"),
            )
            .join(Schedule)
            .join(Slot)
            .join(Order)
            .join(Service)
            .where(extract("month", Order.date_add) == month)
            .group_by(Master.id)
            .cte("master_with_reports")
        )
        query = (
            select(
                Users.last_name,
                Users.first_name,
                master_with_reports.c.total_count,
                # master_with_reports.c.total_sum,
                master_with_reports.c.id,
            )
            .select_from(Users)
            .join(master_with_reports, master_with_reports.c.user_id == Users.id)
        )
        result = await self.session.execute(query)
        return result.mappings().all()


class ScheduleRepository(GenericSQLAlchemyRepository[Schedule, entities.Schedule]):
    model = Schedule

    async def add(self, entity: entities.Schedule) -> entities.Schedule:
        model = self.model.from_entity(entity)
        slots = [Slot.from_entity(slot) for slot in entity.slots]
        model.slots = slots
        self.session.add(model)
        try:
            await self.session.flush()
        except IntegrityError as err:
            raise InsertException(entity=entity, detail=str(err.args))
        return model.to_domain(with_join=True)

    async def find_all(self, **filter_by) -> list[entities.Schedule]:
        query = (
            select(self.model)
            .options(
                joinedload(self.model.master).options(selectinload(Master.services)).options(joinedload(Master.user))
            )
            .filter_by(**filter_by)
        )
        result = await self.session.execute(query)
        return [el.to_domain(with_join=True, child_level=2) for el in result.scalars().all()]

    async def find_one_or_none(self, **filter_by) -> entities.Schedule | None:
        query = (
            select(self.model)
            .options(
                joinedload(self.model.master).options(selectinload(Master.services)).options(joinedload(Master.user))
            )
            .filter_by(**filter_by)
        )
        result = await self.session.execute(query)
        scalar = result.scalar_one_or_none()
        return scalar.to_domain(with_join=True, child_level=2) if scalar else None

    async def find_one_with_consumables(self, **filter_by):
        query = (
            select(self.model)
            .options(
                joinedload(self.model.master).options(selectinload(Master.services)).options(joinedload(Master.user))
            )
            .filter_by(**filter_by)
        )
        result = await self.session.execute(query)
        scalar = result.scalar_one_or_none()
        return scalar.to_domain(with_join=True, child_level=3) if scalar else None

    async def get_day_for_master(self, **filter_by) -> list[date]:
        query = select(self.model.day.distinct()).filter_by(**filter_by).order_by(self.model.day)
        execute_result = await self.session.execute(query)
        result = execute_result.scalars().all()
        return list(result)

    # query = (
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

    async def find_master_services_by_schedule(self, schedule_id: int) -> list[int]:
        query = select(Service.id).join(Service.masters).join(Master.schedules).where(Schedule.id == schedule_id)
        result = await self.session.execute(query)
        # return [el.to_domain(with_join=True) for el in result.scalars().all()]
        return result.scalars().all()

    async def find_one_or_none_slot(self, slot_id: int) -> entities.Slot | None:
        query = select(Slot).filter_by(id=slot_id)
        result = await self.session.execute(query)
        scalar = result.scalar_one_or_none()
        return scalar.to_domain(with_join=True) if scalar else None

    async def find_occupied_slots(self, schedule_id: int) -> list[Slot]:
        query = (
            select(Slot)
            .join(Slot.orders)
            .where(
                and_(
                    Slot.schedule_id == schedule_id,
                    or_(Order.status != OrderStatus.CANCELLED.value, Order.status == None),
                )
            )
        )
        result = await self.session.execute(query)
        return [el.to_domain() for el in result.scalars().all()]


class SlotRepository(GenericSQLAlchemyRepository[Slot, entities.Slot]):
    model = Slot

    async def find_one_or_none(self, **filter_by) -> entities.Slot | None:
        query = select(self.model).options(joinedload(self.model.schedule)).filter_by(**filter_by)
        result = await self.session.execute(query)
        scalar = result.scalar_one_or_none()
        return scalar.to_domain(with_join=True) if scalar else None

    async def find_all(self, **filter_by) -> list[entities.Slot]:
        # query = select(self.model).options(joinedload(Slot.schedule)).filter_by(**filter_by)
        # query = select(self.model).join(Slot.schedule).filter_by(**filter_by)
        query = select(self.model).join(Slot.schedule).options(contains_eager(Slot.schedule)).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [el.to_domain(with_join=True) for el in result.scalars().all()]


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

    async def update_photo(self, entity: entities.Order, photo_after, photo_before):
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


class ServiceQueryRepository(GenericSQLAlchemyQueryRepository[Service]):
    async def find_all(self, **filter_by) -> list[ServiceDTO]:
        query = select(Service).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [
            service_to_detail_dto_mapper(el) for el in result.scalars().all()
        ]


class MasterQueryRepository(GenericSQLAlchemyQueryRepository[Master]):
    async def find_all(self, **filter_by) -> list[MasterDetailDTO]:
        query = (
            select(Master)
            .options(selectinload(Master.services)).options(joinedload(Master.user))
            .filter_by(**filter_by)
        )
        result = await self.session.execute(query)
        return [
            master_to_detail_dto_mapper(el) for el in result.scalars().all()
        ]

    async def get_all_user_to_add_masters(self):
        query = select(Users).where(~Users.master.has())
        result = await self.session.execute(query)
        return [user_to_detail_dto_mapper(el) for el in result.scalars().all()]


class ScheduleQueryRepository(GenericSQLAlchemyQueryRepository[Schedule]):
    async def find_all(self, **filter_by) -> list[ScheduleDetailDTO]:
        query = (
            select(Schedule)
            .options(
                joinedload(Schedule.master)
                .options(selectinload(Master.services))
                .options(joinedload(Master.user))
            )
            .filter_by(**filter_by)
        )
        result = await self.session.execute(query)
        return [
            schedule_to_detail_dto_mapper(el) for el in result.scalars().all()
        ]


class OrderQueryRepository(GenericSQLAlchemyQueryRepository[Order]):
    async def find_all(self, **filter_by) -> list[OrderDetailDTO]:
        query = (
            select(Order)
            .options(
                joinedload(Order.slot, innerjoin=True)
                .joinedload(Slot.schedule, innerjoin=True)
                .options(
                    joinedload(Schedule.master, innerjoin=True)
                    .options(joinedload(Master.user, innerjoin=True))
                    .options(selectinload(Master.services))
                )
            )
            .options(joinedload(Order.service, innerjoin=True))
            .options(joinedload(Order.user, innerjoin=True))
            .filter_by(**filter_by)
        )
        result = await self.session.execute(query)
        return [order_to_detail_dto_mapper(el) for el in result.scalars().all()]
