from datetime import date, time
from typing import Annotated

from pydantic import Field, field_serializer

from src.presentation.api.base.base_schema import BaseSchema
from src.presentation.api.users.schema import AllUserSchema

slot_type = Annotated[str, Field(pattern=r"^(?:[01][0-9]|2?[0-3]):[0-5]{1}\d{1}$")]


# class InventoryAddSchema(BaseSchema):
#     name: str
#     unit: str
#     stock_count: PositiveInt
#
#
# class InventoryUpdateSchema(BaseSchema):
#     name: str | None = None
#     unit: str | None = None
#     stock_count: PositiveInt | None = None
#
#
# class InventorySchema(InventoryAddSchema):
#     id: int


class ServiceSchema(BaseSchema):
    id: int
    name: str
    description: str
    price: int


class MasterAddSchema(BaseSchema):
    description: str
    user_id: int
    services: str


class MasterSchema(BaseSchema):
    id: int
    description: str
    user: AllUserSchema
    services: list[ServiceSchema]


class MasterWithoutServiceSchema(BaseSchema):
    id: int
    description: str
    user: AllUserSchema


class MasterReportSchema(BaseSchema):
    id: int
    last_name: str
    first_name: str
    total_count: int
    total_sum: int


class ScheduleAddSchema(BaseSchema):
    day: date
    service_id: int
    master_id: int


class ScheduleSchema(BaseSchema):
    id: int
    day: date
    service: ServiceSchema
    master: MasterWithoutServiceSchema


class MasterDaysSchema(BaseSchema):
    days: list[date]


class SlotsTimeSchema(BaseSchema):
    slots: list[slot_type]


class ScheduleDay(BaseSchema):
    day: date


class SlotSchema(BaseSchema):
    id: int
    time_start: time
    schedule: ScheduleDay

    @field_serializer("time_start")
    def serialize_time_start(self, time_start: time, _info):
        return time_start.strftime("%H:%M")


class SlotCreateSchema(BaseSchema):
    time_start: slot_type
    schedule_id: int


class SlotUpdateSchema(BaseSchema):
    time_start: slot_type
