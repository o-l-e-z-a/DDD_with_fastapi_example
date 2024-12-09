from datetime import date
from typing import Annotated

from pydantic import Field

from src.presentation.api.base.base_schema import BaseSchema
from src.presentation.api.schedules.schema import ServiceSchema, SlotCreateSchema, SlotSchema
from src.presentation.api.users.schema import AllUserSchema

int_ge_0 = Annotated[int,  Field(ge=0)]


class OrderCreateSchema(BaseSchema):
    point: int_ge_0 | None = 0
    promotion_code: str | None = '0'
    slot: SlotCreateSchema


class OrderUpdatePhotoSchema(BaseSchema):
    photo_before: str
    photo_after: str


class OrderSchema(BaseSchema):
    id: int
    date_add: date
    point_uses: int_ge_0
    promotion_sale: int_ge_0
    total_amount: int_ge_0
    slot: SlotSchema
    # photo_before_path: str | None


class AllOrderSchema(OrderSchema):
    user: AllUserSchema


class TotalAmountSchema(BaseSchema):
    total_amount: int_ge_0
    point_uses: int_ge_0
    promotion_sale: int_ge_0
    errors: list[str] = Field(default_factory=list)


class TotalAmountCreateSchema(BaseSchema):
    point: int_ge_0 | None = 0
    promotion_code: str | None = '0'
    schedule_id: int


class OrderReportSchema(BaseSchema):
    id: int
    name: str
    price: int
    total_count: int_ge_0
    total_sum: int_ge_0


class PromotionAddSchema(BaseSchema):
    code: str
    sale: int = Field(..., ge=0, le=100)
    is_active: bool = True
    day_start: date
    day_end: date
    services: list[int]


class PromotionSchema(PromotionAddSchema):
    id: int
    services: list[ServiceSchema]
