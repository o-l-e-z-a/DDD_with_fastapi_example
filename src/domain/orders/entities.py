from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from src.domain.base.entities import BaseEntity
from src.domain.base.values import CountNumber, Name, PositiveIntNumber
from src.domain.orders.values import LESS_POINT_WARNINGS, MINIMUM_BALANCE, MORE_POINT_WARNINGS
from src.domain.schedules.entities import Service


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
            "services_id": [service_id for service_id in self.services_id],
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
    point_uses: CountNumber
    promotion_sale: CountNumber
    total_amount: PositiveIntNumber
    is_payed: bool = False

    @classmethod
    def add(
        cls,
        order_id: int,
        promotion: Promotion | None,
        user_point: UserPoint,
        input_user_point: CountNumber,
        service: Service
    ):
        total_amount_result = TotalAmountDomainService().calculate(
            promotion=promotion,
            user_point=user_point,
            service=service,
            input_user_point=input_user_point,
        )
        order_payment = cls(
            order_id=order_id,
            point_uses=CountNumber(total_amount_result.point_uses),
            promotion_sale=CountNumber(total_amount_result.promotion_sale),
            total_amount=PositiveIntNumber(total_amount_result.total_amount),
        )
        return order_payment

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "point_uses": self.point_uses.as_generic_type(),
            "promotion_sale": self.promotion_sale.as_generic_type(),
            "total_amount": self.total_amount.as_generic_type(),
            "order_id": self.order_id,
        }


@dataclass()
class TotalAmountResult:
    total_amount: int
    point_uses: int
    promotion_sale: int
    warnings: list[str] = field(default_factory=list)


class TotalAmountDomainService:
    def calculate(
        self, promotion: Promotion | None, user_point: UserPoint, service: Service, input_user_point: CountNumber
    ) -> TotalAmountResult:
        total_amount = service.price.as_generic_type()
        point = input_user_point.as_generic_type()
        warnings = []
        promotion_sale = 0

        if promotion:
            promotion_sale = int(service.price * promotion.sale / 100)
            total_amount -= promotion_sale
        if user_point.count < point:
            point = 0
            warnings.append(LESS_POINT_WARNINGS)
        elif point >= total_amount:
            point = total_amount - MINIMUM_BALANCE
            total_amount = MINIMUM_BALANCE
            warnings.append(MORE_POINT_WARNINGS)
        elif 1 < total_amount - point < MINIMUM_BALANCE:
            diff = point - MINIMUM_BALANCE
            point -= diff
            total_amount -= point
        else:
            total_amount -= point

        return TotalAmountResult(
            total_amount=total_amount, point_uses=point, promotion_sale=promotion_sale, warnings=warnings
        )
