from src.infrastructure.db.models.orders import Promotion, UserPoint
from src.logic.dto.mappers.schedule_mappers import service_to_detail_dto_mapper
from src.logic.dto.order_dto import PromotionDetailDTO, UserPointDTO


def promotion_to_detail_dto_mapper(promotion: Promotion) -> PromotionDetailDTO:
    return PromotionDetailDTO(
        id=promotion.id,
        day_start=promotion.day_start,
        day_end=promotion.day_end,
        code=promotion.code,
        sale=promotion.sale,
        is_active=promotion.is_active,
        services=[service_to_detail_dto_mapper(service) for service in promotion.services],
    )


def user_point_dto_mapper(user_point: UserPoint) -> UserPointDTO:
    return UserPointDTO(
        count=user_point.count,
    )
