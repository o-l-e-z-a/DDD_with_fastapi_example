from datetime import date

from pydantic import Field

from src.presentation.api.base.base_schema import BaseSchema, int_ge_0
from src.presentation.api.schedules.schema import ServiceSchema


class TotalAmountSchema(BaseSchema):
    total_amount: int_ge_0
    point_uses: int_ge_0
    promotion_sale: int_ge_0
    errors: list[str] = Field(default_factory=list)


class TotalAmountCreateSchema(BaseSchema):
    point: int_ge_0 | None = 0
    promotion_code: str | None = "0"
    schedule_id: int


class PromotionAddSchema(BaseSchema):
    code: str = Field(..., max_length=15)
    sale: int = Field(..., ge=0, lt=100)
    is_active: bool = True
    day_start: date
    day_end: date
    services_id: list[int]


class PromotionSchema(PromotionAddSchema):
    id: int


class UserPointSchema(BaseSchema):
    count: int


class PromotionDetailSchema(BaseSchema):
    id: int
    code: str = Field(..., max_length=15)
    sale: int = Field(..., ge=0, lt=100)
    is_active: bool = True
    day_start: date
    day_end: date
    services: list[ServiceSchema]
