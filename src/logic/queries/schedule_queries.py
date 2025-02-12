from pydantic import PositiveInt

from src.logic.queries.base import BaseQuery


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


class GetMasterScheduleDaysQuery(BaseQuery):
    schedule_id: PositiveInt
    master_id: PositiveInt


class GetUserOrdersQuery(BaseQuery):
    user_id: PositiveInt
