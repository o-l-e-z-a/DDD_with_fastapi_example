from datetime import date

from sqlalchemy import and_, extract, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy_file import File
from sqlalchemy_file.exceptions import ContentTypeValidationError

from src.domain.schedules import entities
from src.domain.schedules.entities import OrderStatus
from src.infrastructure.db.exceptions import InsertException, UpdateException
from src.infrastructure.db.models.schedules import Master, Order, Schedule, Service, Slot
from src.infrastructure.db.models.users import Users
from src.infrastructure.db.repositories.base import GenericSQLAlchemyQueryRepository, GenericSQLAlchemyRepository
from src.logic.dto.mappers.schedule_mappers import (
    master_to_detail_dto_mapper,
    order_to_detail_dto_mapper,
    schedule_to_detail_dto_mapper,
    schedule_to_short_dto_mapper,
    service_to_detail_dto_mapper,
    slot_to_short_dto_mapper,
    user_to_detail_dto_mapper,
)
from src.logic.dto.schedule_dto import (
    MasterDetailDTO,
    MasterReportDTO,
    OrderDetailDTO,
    ScheduleDetailDTO,
    ScheduleShortDTO,
    ServiceDTO,
    ServiceReportDTO,
    SlotShortDTO,
)
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
        return model.to_domain()

    async def find_one_or_none(self, **filter_by) -> entities.Master | None:
        query = select(self.model).options(selectinload(self.model.services)).filter_by(**filter_by)
        result = await self.session.execute(query)
        scalar = result.scalar_one_or_none()
        return scalar.to_domain() if scalar else None


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
        return model.to_domain()

    async def find_master_services_by_schedule(self, schedule_id: int) -> list[int]:
        query = select(Service.id).join(Service.masters).join(Master.schedules).where(Schedule.id == schedule_id)
        result = await self.session.execute(query)
        # return [el.to_domain(with_join=True) for el in result.scalars().all()]
        return list(result.scalars().all())

    async def find_one_or_none_slot(self, slot_id: int) -> entities.Slot | None:
        query = select(Slot).filter_by(id=slot_id)
        result = await self.session.execute(query)
        scalar = result.scalar_one_or_none()
        return scalar.to_domain() if scalar else None

    async def find_occupied_slots(self, schedule_id: int) -> list[entities.Slot]:
        query = (
            select(Slot)
            .join(Slot.orders)
            .where(
                and_(
                    Slot.schedule_id == schedule_id,
                    or_(Order.status != OrderStatus.CANCELLED.value, Order.status == None),  # noqa: E711
                )
            )
        )
        result = await self.session.execute(query)
        return [el.to_domain() for el in result.scalars().all()]


class OrderRepository(GenericSQLAlchemyRepository[Order, entities.Order]):
    model = Order

    async def find_one_or_none(self, **filter_by) -> entities.Order | None:
        query = self.get_query_to_find_all(**filter_by)
        result = await self.session.execute(query)
        scalar = result.scalar_one_or_none()
        return scalar.to_domain() if scalar else None

    def get_query_to_find_all(self, **filter_by):
        query = select(self.model).options(joinedload(self.model.user, innerjoin=True)).filter_by(**filter_by)
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
    async def find_all(self, services_id: list[int] | None = None) -> list[ServiceDTO]:
        query = select(Service)
        if services_id:
            query = query.where(Service.id.in_(services_id))
        result = await self.session.execute(query)
        return [service_to_detail_dto_mapper(el) for el in result.scalars().all()]

    async def get_services_by_master(self, master_id: int) -> list[ServiceDTO]:
        query = select(Service).join(Service.masters).where(Master.id == master_id)
        result = await self.session.execute(query)
        return [service_to_detail_dto_mapper(el) for el in result.scalars().all()]


class MasterQueryRepository(GenericSQLAlchemyQueryRepository[Master]):
    async def find_one_or_none(self, **filter_by) -> MasterDetailDTO | None:
        query = (
            select(Master)
            .options(joinedload(Master.user))
            .options(selectinload(Master.services))
            .filter_by(**filter_by)
        )
        result = await self.session.execute(query)
        scalar = result.scalar_one_or_none()
        return master_to_detail_dto_mapper(scalar) if scalar else None

    async def find_all(self, **filter_by) -> list[MasterDetailDTO]:
        query = (
            select(Master)
            .options(selectinload(Master.services))
            .options(joinedload(Master.user))
            .filter_by(**filter_by)
        )
        result = await self.session.execute(query)
        return [master_to_detail_dto_mapper(el) for el in result.scalars().all()]

    async def get_all_user_to_add_masters(self) -> list[UserDetailDTO]:
        query = select(Users).where(~Users.master.has())
        result = await self.session.execute(query)
        return [user_to_detail_dto_mapper(el) for el in result.scalars().all()]

    async def filter_by_service(self, service_id: int) -> list[MasterDetailDTO]:
        query = (
            select(Master)
            .options(joinedload(Master.user))
            .options(selectinload(Master.services))
            .where(Service.id == service_id)
        )
        result = await self.session.execute(query)
        return [master_to_detail_dto_mapper(el) for el in result.scalars().all()]

    async def get_order_report_by_master(self, month: int | None = None) -> list[MasterReportDTO]:
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
        return [MasterReportDTO(**el) for el in result.mappings().all()]


class ScheduleQueryRepository(GenericSQLAlchemyQueryRepository[Schedule]):
    async def find_all(self, **filter_by) -> list[ScheduleDetailDTO]:
        query = (
            select(Schedule)
            .options(
                joinedload(Schedule.master).options(selectinload(Master.services)).options(joinedload(Master.user))
            )
            .filter_by(**filter_by)
        )
        result = await self.session.execute(query)
        return [schedule_to_detail_dto_mapper(el) for el in result.scalars().all()]

    async def find_occupied_slots(self, schedule_id: int) -> list[SlotShortDTO]:
        query = (
            select(Slot)
            .join(Slot.orders)
            .where(
                and_(
                    Slot.schedule_id == schedule_id,
                    or_(Order.status != OrderStatus.CANCELLED.value, Order.status == None),  # noqa: E711
                )
            )
        )
        result = await self.session.execute(query)
        return [slot_to_short_dto_mapper(el) for el in result.scalars().all()]

    async def find_free_slots(self, schedule_id: int) -> list[SlotShortDTO]:
        query = (
            select(Slot)
            .join(Slot.orders, isouter=True)
            .where(
                and_(
                    Slot.schedule_id == schedule_id,
                    ~Slot.orders.any(),  # noqa: E711
                )
            )
        )
        result = await self.session.execute(query)
        return [slot_to_short_dto_mapper(el) for el in result.scalars().all()]

    async def get_schedule_for_master(self, master_id: int) -> list[ScheduleShortDTO]:
        query = select(Schedule).filter_by(master_id=master_id).order_by(Schedule.day)
        result = await self.session.execute(query)
        return [schedule_to_short_dto_mapper(el) for el in result.scalars().all()]


class OrderQueryRepository(GenericSQLAlchemyQueryRepository[Order]):
    async def find_one_or_none(self, **filter_by) -> OrderDetailDTO | None:
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
        scalar = result.scalar_one_or_none()
        return order_to_detail_dto_mapper(scalar) if scalar else None

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

    async def get_order_report_by_service(self) -> list[ServiceReportDTO]:
        query = (
            select(
                Service.id,
                Service.name,
                Service.price,
                func.count(Service.id).label("total_count"),
                # func.sum(Order.total_amount).label("total_sum"),
            )
            .join(Order)
            .group_by(Service.id)
        )
        result = await self.session.execute(query)
        return [ServiceReportDTO(**el) for el in result.mappings().all()]
