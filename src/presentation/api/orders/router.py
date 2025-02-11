from dataclasses import asdict

from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, status

from src.logic.dto.order_dto import (
    PromotionAddDTO,
    PromotionUpdateDTO,
    TotalAmountDTO,
)
from src.logic.exceptions.base_exception import NotFoundLogicException
from src.logic.services.order_service import OrderService, PromotionService
from src.presentation.api.dependencies import CurrentUser, get_order_service, get_promotion_service
from src.presentation.api.exceptions import (
    NotFoundHTTPException,
)
from src.presentation.api.orders.schema import (
    PromotionAddSchema,
    PromotionSchema,
    TotalAmountCreateSchema,
    TotalAmountSchema,
)

router = APIRouter(route_class=DishkaRoute, prefix="/api", tags=["order"])


@router.post("/total_amount/")
async def get_total_amount(
    total_amount_data: TotalAmountCreateSchema,
    user: CurrentUser,
    order_service: OrderService = Depends(get_order_service),
) -> TotalAmountSchema:
    try:
        total_amount = await order_service.get_total_amount(
            total_amount_dto=TotalAmountDTO(**total_amount_data.model_dump()), user=user
        )
    except NotFoundLogicException as err:
        raise NotFoundHTTPException(detail=err.title)
    return TotalAmountSchema(**asdict(total_amount))


@router.get("/promotions/")
async def get_promotions(promotion_service: PromotionService = Depends(get_promotion_service)) -> list[PromotionSchema]:
    results = await promotion_service.get_promotions()
    promotion_schemas = [PromotionSchema.model_validate(promotion.to_dict()) for promotion in results]
    return promotion_schemas


@router.post("/promotion/add/", status_code=status.HTTP_201_CREATED)
async def add_promotion(
    promotion_data: PromotionAddSchema, promotion_service: PromotionService = Depends(get_promotion_service)
) -> PromotionSchema:
    try:
        promotion = await promotion_service.add_promotion(promotion_data=PromotionAddDTO(**promotion_data.model_dump()))
    except NotFoundLogicException as err:
        raise NotFoundHTTPException(detail=err.title)
    promotion_schema = PromotionSchema.model_validate(promotion.to_dict())
    return promotion_schema


@router.patch("/promotion/{promotion_id}/update/")
async def patch_promotion(
    promotion_id: int,
    promotion_data: PromotionAddSchema,
    promotion_service: PromotionService = Depends(get_promotion_service),
) -> PromotionSchema:
    try:
        promotion = await promotion_service.update_promotion(
            promotion_data=PromotionUpdateDTO(**promotion_data.model_dump(), promotion_id=promotion_id)
        )
    except NotFoundLogicException as err:
        raise NotFoundHTTPException(detail=err.title)
    promotion_schema = PromotionSchema.model_validate(promotion.to_dict())
    return promotion_schema


@router.delete("/promotion/{promotion_id}/delete/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_promotion(promotion_id: int, promotion_service: PromotionService = Depends(get_promotion_service)):
    try:
        await promotion_service.delete_promotion(promotion_id=promotion_id)
    except NotFoundLogicException as err:
        raise NotFoundHTTPException(detail=err.title)
