from dataclasses import dataclass

from pydantic import PositiveInt

from src.infrastructure.db.uows.schedule_uow import SQLAlchemyScheduleQueryUnitOfWork
from src.logic.dto.schedule_dto import (
    MasterDetailDTO,
    MasterReportDTO,
    OrderDetailDTO,
    ScheduleDetailDTO,
    ServiceDTO,
    ServiceReportDTO,
    SlotShortDTO, ScheduleShortDTO,
)
from src.logic.dto.user_dto import UserDetailDTO
from src.logic.queries.base import BaseQuery, QueryHandler


class GetAllServiceQuery(BaseQuery): ...


class GetAllMasterQuery(BaseQuery): ...


class GetAllSchedulesQuery(BaseQuery): ...


class GetAllOrdersQuery(BaseQuery): ...


class GetAllUsersToAddMasterQuery(BaseQuery): ...


class GetMasterReportQuery(BaseQuery): ...


class GetServiceReportQuery(BaseQuery): ...


class GetMasterForServiceQuery(BaseQuery):
    service_id: PositiveInt


class GetServiceForMasterQuery(BaseQuery):
    master_id: PositiveInt


class GetMasterScheduleQuery(BaseQuery):
    master_id: PositiveInt


class GetScheduleSlotsQuery(BaseQuery):
    schedule_id: PositiveInt


class GetUserOrdersQuery(BaseQuery):
    user_id: PositiveInt


@dataclass(frozen=True)
class GetAllServiceQueryHandler(QueryHandler[GetAllServiceQuery, list[ServiceDTO]]):
    uow: SQLAlchemyScheduleQueryUnitOfWork

    async def handle(self, query: GetAllServiceQuery) -> list[ServiceDTO]:
        async with self.uow:
            results = await self.uow.services.find_all()
        return results


@dataclass(frozen=True)
class GetAllMasterQueryHandler(QueryHandler[GetAllMasterQuery, list[MasterDetailDTO]]):
    uow: SQLAlchemyScheduleQueryUnitOfWork

    async def handle(self, query: GetAllMasterQuery) -> list[MasterDetailDTO]:
        async with self.uow:
            results = await self.uow.masters.find_all()
        return results


@dataclass(frozen=True)
class GetAllSchedulesQueryHandler(QueryHandler[GetAllSchedulesQuery, list[ScheduleDetailDTO]]):
    uow: SQLAlchemyScheduleQueryUnitOfWork

    async def handle(self, query: GetAllSchedulesQuery) -> list[ScheduleDetailDTO]:
        async with self.uow:
            results = await self.uow.schedules.find_all()
        return results


@dataclass(frozen=True)
class GetAllOrdersQueryHandler(QueryHandler[GetAllOrdersQuery, list[OrderDetailDTO]]):
    uow: SQLAlchemyScheduleQueryUnitOfWork

    async def handle(self, query: GetAllOrdersQuery) -> list[OrderDetailDTO]:
        async with self.uow:
            results = await self.uow.orders.find_all()
        return results


@dataclass(frozen=True)
class GetAllUsersToAddMasterQueryHandler(QueryHandler[GetAllUsersToAddMasterQuery, list[UserDetailDTO]]):
    uow: SQLAlchemyScheduleQueryUnitOfWork

    async def handle(self, query: GetAllUsersToAddMasterQuery) -> list[UserDetailDTO]:
        async with self.uow:
            results = await self.uow.masters.get_all_user_to_add_masters()
        return results


@dataclass(frozen=True)
class GetMasterScheduleQueryHandler(QueryHandler[GetMasterScheduleQuery, list[ScheduleShortDTO]]):
    uow: SQLAlchemyScheduleQueryUnitOfWork

    async def handle(self, query: GetMasterScheduleQuery) -> list[ScheduleShortDTO]:
        async with self.uow:
            results = await self.uow.schedules.get_schedule_for_master(master_id=query.master_id)
        return results


@dataclass(frozen=True)
class GetMasterForServiceQueryHandler(QueryHandler[GetMasterForServiceQuery, list[MasterDetailDTO]]):
    uow: SQLAlchemyScheduleQueryUnitOfWork

    async def handle(self, query: GetMasterForServiceQuery) -> list[MasterDetailDTO]:
        async with self.uow:
            results = await self.uow.masters.filter_by_service(service_id=query.service_id)
        return results


@dataclass(frozen=True)
class GetServiceForMasterQueryHandler(QueryHandler[GetServiceForMasterQuery, list[ServiceDTO]]):
    uow: SQLAlchemyScheduleQueryUnitOfWork

    async def handle(self, query: GetServiceForMasterQuery) -> list[ServiceDTO]:
        async with self.uow:
            results = await self.uow.services.get_services_by_master(master_id=query.master_id)
        return results


@dataclass(frozen=True)
class GetScheduleSlotsQueryHandler(QueryHandler[GetScheduleSlotsQuery, list[SlotShortDTO]]):
    uow: SQLAlchemyScheduleQueryUnitOfWork

    async def handle(self, query: GetScheduleSlotsQuery) -> list[SlotShortDTO]:
        async with self.uow:
            results = await self.uow.schedules.find_occupied_slots(schedule_id=query.schedule_id)
        return results


@dataclass(frozen=True)
class GetUserOrdersQueryHandler(QueryHandler[GetUserOrdersQuery, list[OrderDetailDTO]]):
    uow: SQLAlchemyScheduleQueryUnitOfWork

    async def handle(self, query: GetUserOrdersQuery) -> list[OrderDetailDTO]:
        async with self.uow:
            orders = await self.uow.orders.find_all(user_id=query.user_id)
        return orders


@dataclass(frozen=True)
class GetMasterReportQueryHandler(QueryHandler[GetMasterReportQuery, list[MasterReportDTO]]):
    uow: SQLAlchemyScheduleQueryUnitOfWork

    async def handle(self, query: GetMasterReportQuery) -> list[MasterReportDTO]:
        async with self.uow:
            orders = await self.uow.masters.get_order_report_by_master(month=1)
        return orders


@dataclass(frozen=True)
class GetServiceReportQueryHandler(QueryHandler[GetServiceReportQuery, list[ServiceReportDTO]]):
    uow: SQLAlchemyScheduleQueryUnitOfWork

    async def handle(self, query: GetServiceReportQuery) -> list[ServiceReportDTO]:
        async with self.uow:
            orders = await self.uow.orders.get_order_report_by_service()
        return orders
