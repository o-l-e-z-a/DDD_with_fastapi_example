from dataclasses import dataclass
from datetime import date, datetime
from typing import Annotated

from pydantic import Field

from src.logic.dto.base_dto import BaseDTO

int_ge_0 = Annotated[int, Field(ge=0)]
slot_type = Annotated[str, Field(pattern=r"^(?:[01][0-9]|2?[0-3]):[0-5]\d$")]


@dataclass(frozen=True)
class TotalAmountDTO(BaseDTO):
    service_id: int
    user_id: int
    point: int_ge_0 | None = 0
    promotion_code: str | None = "0"


@dataclass(frozen=True)
class ServiceDTO(BaseDTO):
    id: int
    name: str
    description: str
    price: int


@dataclass(frozen=True)
class PromotionDetailDTO(BaseDTO):
    id: int
    code: str
    sale: int
    is_active: bool
    day_start: date
    day_end: date
    services: list[ServiceDTO]


@dataclass(frozen=True)
class UserPointDTO(BaseDTO):
    count: int


@dataclass(frozen=True)
class OrderPaymentDetailDTO(BaseDTO):
    id: int
    order_id: int
    total_amount: int
    point_uses: int
    promotion_sale: int
    is_payed: bool


@dataclass(frozen=True)
class OrderShortDTO(BaseDTO):
    id: int
    date_add: datetime
    service_id: int
    user_id: int
    slot_id: int
