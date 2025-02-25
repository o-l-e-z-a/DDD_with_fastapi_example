from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from src.domain.base.entities import BaseEntity
from src.domain.base.values import CountNumber, Name, PositiveIntNumber
from src.domain.orders.service import TotalAmountDomainService, TotalAmountResult


@dataclass()
class Promotion(BaseEntity):
    code: Name
    sale: PositiveIntNumber
    is_active: bool
    day_start: date
    day_end: date
    services_id: list[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "code": self.code.as_generic_type(),
            "sale": self.sale.as_generic_type(),
            "is_active": self.is_active,
            "day_start": self.day_start,
            "day_end": self.day_end,
            "services_id": self.services_id,
        }


@dataclass()
class UserPoint(BaseEntity):
    user_id: int
    count: CountNumber = CountNumber(0)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "count": self.count.as_generic_type(),
            "user_id": self.user_id,
        }


@dataclass()
class OrderPayment(BaseEntity):
    order_id: int
    total_amount: PositiveIntNumber
    point_uses: CountNumber = CountNumber(0)
    promotion_sale: CountNumber = CountNumber(0)
    is_payed: bool = False

    @classmethod
    def add(cls, order_id: int, service_price: int):
        order_payment = cls(
            order_id=order_id,
            total_amount=PositiveIntNumber(service_price),
        )
        return order_payment

    def calculate_amount(
        self, promotion_sale: int | None, user_point_count: int | None, input_user_point: int
    ) -> TotalAmountResult:
        total_amount_result = TotalAmountDomainService().calculate(
            promotion_sale=promotion_sale,
            user_point_count=user_point_count,
            service_price=self.total_amount.as_generic_type(),
            input_user_point=input_user_point,
        )
        return total_amount_result

    def pay(self, promotion_sale: int | None, user_point_count: int | None, input_user_point: int):
        total_amount_result = self.calculate_amount(promotion_sale, user_point_count, input_user_point)
        self.point_uses = CountNumber(total_amount_result.point_uses)
        self.promotion_sale = CountNumber(total_amount_result.promotion_sale)
        self.total_amount = PositiveIntNumber(total_amount_result.total_amount)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "point_uses": self.point_uses.as_generic_type(),
            "promotion_sale": self.promotion_sale.as_generic_type(),
            "total_amount": self.total_amount.as_generic_type(),
            "order_id": self.order_id,
        }
