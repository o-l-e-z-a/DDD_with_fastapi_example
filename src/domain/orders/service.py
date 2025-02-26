from __future__ import annotations

from dataclasses import dataclass, field

from src.domain.orders.values import LESS_POINT_WARNINGS, MINIMUM_BALANCE, MORE_POINT_WARNINGS


class TotalAmountDomainService:
    @staticmethod
    def calculate(
        promotion_sale: int | None, user_point_count: int | None, service_price: int, input_user_point: int
    ) -> TotalAmountResult:
        total_amount = service_price
        point = input_user_point
        warnings = []
        promotion_sale_value = 0

        if promotion_sale:
            promotion_sale_value = int(service_price * promotion_sale / 100)
            total_amount -= promotion_sale_value
        if user_point_count < point:
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
            total_amount=total_amount, point_uses=point, promotion_sale=promotion_sale_value, warnings=warnings
        )


@dataclass()
class TotalAmountResult:
    total_amount: int
    point_uses: int
    promotion_sale: int
    warnings: list[str] = field(default_factory=list)
