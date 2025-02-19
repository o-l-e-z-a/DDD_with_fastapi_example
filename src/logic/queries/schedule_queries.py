from dataclasses import dataclass
from datetime import date

from pydantic import PositiveInt

from src.infrastructure.db.uows.schedule_uow import SQLAlchemyScheduleQueryUnitOfWork
from src.logic.dto.schedule_dto import ServiceDTO, MasterDetailDTO, ScheduleDetailDTO, OrderDetailDTO, ScheduleShortDTO
from src.logic.dto.user_dto import UserDetailDTO
from src.logic.queries.base import BaseQuery, QueryHandler


class GetAllServiceQuery(BaseQuery):
    ...


class GetAllMasterQuery(BaseQuery):
    ...


class GetAllSchedulesQuery(BaseQuery):
    ...


class GetAllOrdersQuery(BaseQuery):
    ...


class GetAllUsersToAddMasterQuery(BaseQuery):
    ...


class GetMasterReportQuery(BaseQuery):
    ...


class GetServiceReportQuery(BaseQuery):
    ...


class GetMasterForServiceQuery(BaseQuery):
    service_id: PositiveInt


class GetMasterDaysQuery(BaseQuery):
    master_id: PositiveInt


class GetScheduleSlotsQuery(BaseQuery):
    schedule_id: PositiveInt


class GetDaysForMasterAndServiceQuery(BaseQuery):
    service_id: PositiveInt
    master_id: PositiveInt


class GetUserOrdersQuery(BaseQuery):
    user_id: PositiveInt


@dataclass(frozen=True)
class GetAllServiceQueryHandler(QueryHandler[GetAllServiceQuery, list[ServiceDTO]]):
    uow: SQLAlchemyScheduleQueryUnitOfWork

    async def handle(self, query: GetAllServiceQuery) -> list[ServiceDTO]:
        async with self.uow:
            services = await self.uow.services.find_all()
        return services


@dataclass(frozen=True)
class GetAllMasterQueryHandler(QueryHandler[GetAllMasterQuery, list[MasterDetailDTO]]):
    uow: SQLAlchemyScheduleQueryUnitOfWork

    async def handle(self, query: GetAllMasterQuery) -> list[MasterDetailDTO]:
        async with self.uow:
            services = await self.uow.masters.find_all()
        return services


@dataclass(frozen=True)
class GetAllSchedulesQueryHandler(QueryHandler[GetAllSchedulesQuery, list[ScheduleDetailDTO]]):
    uow: SQLAlchemyScheduleQueryUnitOfWork

    async def handle(self, query: GetAllSchedulesQuery) -> list[ScheduleDetailDTO]:
        async with self.uow:
            services = await self.uow.schedules.find_all()
        return services


@dataclass(frozen=True)
class GetAllOrdersQueryHandler(QueryHandler[GetAllOrdersQuery, list[OrderDetailDTO]]):
    uow: SQLAlchemyScheduleQueryUnitOfWork

    async def handle(self, query: GetAllOrdersQuery) -> list[OrderDetailDTO]:
        async with self.uow:
            services = await self.uow.orders.find_all()
        return services


@dataclass(frozen=True)
class GetAllUsersToAddMasterQueryHandler(QueryHandler[GetAllUsersToAddMasterQuery, list[UserDetailDTO]]):
    uow: SQLAlchemyScheduleQueryUnitOfWork

    async def handle(self, query: GetAllUsersToAddMasterQuery) -> list[UserDetailDTO]:
        async with self.uow:
            services = await self.uow.masters.get_all_user_to_add_masters()
        return services


@dataclass(frozen=True)
class GetMasterDaysQueryHandler(QueryHandler[GetMasterDaysQuery, list[date]]):
    uow: SQLAlchemyScheduleQueryUnitOfWork

    async def handle(self, query: GetMasterDaysQuery) -> list[date]:
        async with self.uow:
            days = await self.uow.schedules.get_day_for_master(master_id=query.master_id)
        return days


@dataclass(frozen=True)
class GetMasterForServiceQueryHandler(QueryHandler[GetMasterForServiceQuery, list[MasterDetailDTO]]):
    uow: SQLAlchemyScheduleQueryUnitOfWork

    async def handle(self, query: GetMasterForServiceQuery) -> list[MasterDetailDTO]:
        async with self.uow:
            masters = await self.uow.masters.filter_by_service(service_id=query.service_id)
        return masters


@dataclass(frozen=True)
class GetDaysForMasterAndServiceQueryHandler(QueryHandler[GetDaysForMasterAndServiceQuery, list[date]]):
    uow: SQLAlchemyScheduleQueryUnitOfWork

    async def handle(self, query: GetDaysForMasterAndServiceQuery) -> list[date]:
        async with self.uow:
            days = await self.uow.schedules.get_day_for_master(master_id=query.master_id, service_id=query.service_id)
        return days
