from datetime import date
from typing import Annotated

from pydantic import Field

from src.logic.dto.base_dto import BaseDTO

int_ge_0 = Annotated[int, Field(ge=0)]
slot_type = Annotated[str, Field(pattern=r"^(?:[01][0-9]|2?[0-3]):[0-5]\d$")]


class TotalAmountDTO(BaseDTO):
    schedule_id: int
    point: int_ge_0 | None = 0
    promotion_code: str | None = "0"


class OrderCreateDTO(BaseDTO):
    total_amount: TotalAmountDTO
    time_start: slot_type


class OrderUpdateDTO(BaseDTO):
    order_id: int
    time_start: slot_type


class PromotionAddDTO(BaseDTO):
    code: str
    sale: int = Field(..., ge=0, le=100)
    is_active: bool = True
    day_start: date
    day_end: date
    services_id: list[int]


class PromotionUpdateDTO(PromotionAddDTO):
    promotion_id: int
