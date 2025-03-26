from datetime import date

from pydantic import Field

from src.presentation.api.base.base_schema import BaseSchema, int_ge_0


class TotalAmountSchema(BaseSchema):
    total_amount: int_ge_0
    point_uses: int_ge_0
    promotion_sale: int_ge_0
    warnings: list[str] = Field(default_factory=list)


class TotalAmountInputSchema(BaseSchema):
    input_point: int_ge_0 | None = 0
    promotion_code: str | None = "0"


class OrderPaymentSchema(BaseSchema):
    order_id: int
    total_amount: int_ge_0
    point_uses: int_ge_0
    promotion_sale: int_ge_0
    is_payed: bool


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
    services: list[int]


class OrderPaymentDetailSchema(BaseSchema):
    id: int
    order_id: int
    total_amount: int_ge_0
    point_uses: int
    promotion_sale: int
    is_payed: bool
