from src.infrastructure.db.models.orders import OrderPayment, Promotion, UserPoint
from src.logic.dto.order_dto import OrderPaymentDetailDTO, PromotionDetailDTO, UserPointDTO


def promotion_to_detail_dto_mapper(promotion: Promotion) -> PromotionDetailDTO:
    return PromotionDetailDTO(
        id=promotion.id,
        day_start=promotion.day_start,
        day_end=promotion.day_end,
        code=promotion.code,
        sale=promotion.sale,
        is_active=promotion.is_active,
        services=[service.service_id for service in promotion.services],
    )


def user_point_dto_mapper(user_point: UserPoint) -> UserPointDTO:
    return UserPointDTO(
        count=user_point.count,
    )


def order_payment_detail_dto_mapper(order_payment: OrderPayment) -> OrderPaymentDetailDTO:
    return OrderPaymentDetailDTO(
        id=order_payment.id,
        order_id=order_payment.order_id,
        total_amount=order_payment.total_amount,
        point_uses=order_payment.point_uses,
        promotion_sale=order_payment.promotion_sale,
        is_payed=order_payment.is_payed,
    )
