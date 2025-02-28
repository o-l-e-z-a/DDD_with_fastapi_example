from __future__ import annotations

from dataclasses import dataclass, field

from src.domain.orders.values import LESS_POINT_WARNINGS, MINIMUM_BALANCE, MORE_POINT_WARNINGS


class TotalAmountDomainService:
    @staticmethod
    def calculate(
        promotion_sale: int | None, user_point_count: int | None, service_price: int, user_point_input: int
    ) -> TotalAmountResult:
        total_amount = service_price
        point = user_point_input
        warnings = []
        promotion_sale_value = 0
        print(f"total_amount={total_amount}, user_point_count: {user_point_count}, point_uses={point}, promotion_sale={promotion_sale_value}, service_price: {service_price}")
        if promotion_sale:
            promotion_sale_value = int(service_price * promotion_sale / 100)
            if 1 < total_amount - promotion_sale_value < MINIMUM_BALANCE:
                promotion_sale_value = total_amount - MINIMUM_BALANCE
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
        print(f"total_amount={total_amount}, user_point_count: {user_point_count}, point_uses={point}, promotion_sale={promotion_sale_value}, service_price: {service_price}")
        return TotalAmountResult(
            total_amount=total_amount, point_uses=point, promotion_sale=promotion_sale_value, warnings=warnings
        )


@dataclass()
class TotalAmountResult:
    total_amount: int
    point_uses: int
    promotion_sale: int
    warnings: list[str] = field(default_factory=list)
