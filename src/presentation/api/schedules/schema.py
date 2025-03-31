from datetime import date, datetime, time

from pydantic import PositiveInt, field_serializer

from src.presentation.api.base.base_schema import BaseSchema, int_ge_0
from src.presentation.api.users.schema import AllUserSchema, UserFIOSchema

# slot_type = Annotated[str, Field(pattern=r"^(?:[01][0-9]|2?[0-3]):[0-5]{1}\d{1}$")]


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
    user_id: int
    services_id: list[int]


class MasterDetailSchema(BaseSchema):
    id: int
    description: str
    user: UserFIOSchema
    services: list[ServiceSchema]


class MasterWithoutServiceSchema(BaseSchema):
    id: int
    description: str
    user: UserFIOSchema


class MasterReportSchema(BaseSchema):
    id: int
    last_name: str
    first_name: str
    total_count: int
    # total_sum: int


class ScheduleAddSchema(BaseSchema):
    day: date
    master_id: int


class ScheduleSchema(BaseSchema):
    id: int
    day: date
    master_id: int


class ScheduleDetailSchema(BaseSchema):
    id: int
    day: date
    master: MasterWithoutServiceSchema


class MasterDaysSchema(BaseSchema):
    days: list[date]


class SlotTimeSchema(BaseSchema):
    id: int
    time_start: time


class ScheduleDay(BaseSchema):
    id: int
    day: date


class SlotSchema(BaseSchema):
    id: int
    time_start: time
    schedule: ScheduleDetailSchema

    @field_serializer("time_start")
    def serialize_time_start(self, time_start: time, _info):
        return time_start.strftime("%H:%M")


class OrderUpdateSchema(BaseSchema):
    slot_id: PositiveInt


class OrderCreateSchema(BaseSchema):
    # point: int_ge_0 | None = 0
    # promotion_code: str | None = "0"
    slot_id: PositiveInt
    service_id: PositiveInt


class OrderUpdatePhotoSchema(BaseSchema):
    photo_before: str
    photo_after: str


class OrderSchema(BaseSchema):
    id: int
    date_add: datetime
    service_id: int
    user_id: int
    slot_id: int
    photo_before_path: str | None
    photo_after_path: str | None

    @field_serializer("date_add")
    def serialize_date_add(self, date_add: datetime, _info):
        return date_add.strftime("%Y-%m-%dT%H:%M")


class OrderDetailSchema(BaseSchema):
    id: int
    date_add: datetime
    service: ServiceSchema
    slot: SlotSchema
    photo_before_path: str | None
    photo_after_path: str | None

    @field_serializer("date_add")
    def serialize_date_add(self, date_add: datetime, _info):
        return date_add.strftime("%Y-%m-%dT%H:%M")


class AllOrderDetailSchema(OrderDetailSchema):
    user: AllUserSchema


class OrderReportSchema(BaseSchema):
    id: int
    name: str
    price: int
    total_count: int_ge_0
    # total_sum: int_ge_0
