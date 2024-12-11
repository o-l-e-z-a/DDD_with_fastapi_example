from dataclasses import asdict

from fastapi import APIRouter, Depends, UploadFile, status
from fastapi_cache.decorator import cache

from src.domain.schedules.exceptions import SlotOccupiedException
from src.infrastructure.db.exceptions import UpdateException
from src.logic.dto.order_dto import (
    OrderCreateDTO,
    OrderUpdateDTO,
    PhotoDTO,
    PromotionAddDTO,
    PromotionUpdateDTO,
    TotalAmountDTO,
)
from src.logic.exceptions.base_exception import NotFoundLogicException
from src.logic.exceptions.order_exceptions import NotUserOrderLogicException
from src.logic.services.order_service import OrderService, PromotionService
from src.presentation.api.dependencies import CurrentUser, get_order_service, get_promotion_service
from src.presentation.api.exceptions import (
    CannotUpdateDataToDatabase,
    NotCorrectDataHTTPException,
    NotFoundHTTPException,
    NotUserOrderException,
)
from src.presentation.api.orders.schema import (
    AllOrderSchema,
    OrderCreateSchema,
    OrderReportSchema,
    OrderSchema,
    PromotionAddSchema,
    PromotionSchema,
    TotalAmountCreateSchema,
    TotalAmountSchema,
)
from src.presentation.api.schedules.schema import SlotUpdateSchema

router = APIRouter(prefix="/api", tags=["order"])


@router.get("/all_orders/", description="все заказы для просмотра мастером")
@cache(expire=60)
async def get_all_orders(order_service: OrderService = Depends(get_order_service)) -> list[AllOrderSchema]:
    results = await order_service.get_all_orders()
    order_schemas = [AllOrderSchema.model_validate(order.to_dict()) for order in results]
    return order_schemas


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


@router.get("/orders/", description="все заказы клиента")
@cache(expire=60)
async def get_client_orders(
    user: CurrentUser, order_service: OrderService = Depends(get_order_service)
) -> list[OrderSchema]:
    results = await order_service.get_client_orders(user=user)
    order_schemas = [OrderSchema.model_validate(order.to_dict()) for order in results]
    return order_schemas


@router.post("/order/add/", status_code=status.HTTP_201_CREATED)
async def add_order(
    order_data: OrderCreateSchema,
    user: CurrentUser,
    order_service: OrderService = Depends(get_order_service),
) -> OrderSchema:
    try:
        order = await order_service.add_order(
            order_data=OrderCreateDTO(
                total_amount=TotalAmountDTO(
                    schedule_id=order_data.slot.schedule_id,
                    point=order_data.point,
                    promotion_code=order_data.promotion_code,
                ),
                time_start=order_data.slot.time_start,
            ),
            user=user,
        )
    except NotFoundLogicException as err:
        raise NotFoundHTTPException(detail=err.title)
    except SlotOccupiedException as err:
        raise NotCorrectDataHTTPException(detail=err.title)
    order_schema = OrderSchema.model_validate(order.to_dict())
    # order_create_send_mail_task.delay(order_dict)
    return order_schema


@router.put("/order/{order_id}/update/")
async def update_order(
    order_id: int,
    slot_data: SlotUpdateSchema,
    user: CurrentUser,
    order_service: OrderService = Depends(get_order_service),
) -> OrderSchema:
    try:
        order = await order_service.update_order(
            order_data=OrderUpdateDTO(**slot_data.model_dump(), order_id=order_id), user=user
        )
    except NotFoundLogicException as err:
        raise NotFoundHTTPException(detail=err.title)
    except NotUserOrderLogicException as err:
        raise NotUserOrderException(detail=err.title)
    except SlotOccupiedException as err:
        raise NotCorrectDataHTTPException(detail=err.title)
    order_schema = OrderSchema.model_validate(order.to_dict())
    return order_schema


@router.patch("/order/{order_id}/update_photo/")
async def update_photo(
    order_id: int,
    photo_before: UploadFile,
    photo_after: UploadFile,
    order_service: OrderService = Depends(get_order_service),
) -> OrderSchema:
    photo_before_dto = PhotoDTO(
        file=photo_before.file, filename=photo_before.filename, content_type=photo_before.content_type
    )
    photo_after_dto = PhotoDTO(
        file=photo_after.file, filename=photo_after.filename, content_type=photo_after.content_type
    )
    try:
        order = await order_service.update_order_photos(
            order_id=order_id, photo_before=photo_before_dto, photo_after=photo_after_dto
        )
    except NotFoundLogicException as err:
        raise NotFoundHTTPException(detail=err.title)
    except NotUserOrderLogicException as err:
        raise NotUserOrderException(detail=err.title)
    except UpdateException as err:
        raise CannotUpdateDataToDatabase(detail=err.title)
    order_schema = OrderSchema.model_validate(order.to_dict())
    return order_schema


@router.delete("/order/{order_id}/delete/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: int,
    user: CurrentUser,
    order_service: OrderService = Depends(get_order_service),
):
    try:
        await order_service.delete_order(order_id=order_id, user=user)
    except NotFoundLogicException as err:
        raise NotFoundHTTPException(detail=err.title)
    except NotUserOrderLogicException as err:
        raise NotUserOrderException(detail=err.title)


@router.post("/service_report/")
async def get_service_report(order_service: OrderService = Depends(get_order_service)) -> list[OrderReportSchema]:
    report_results = await order_service.get_service_report()
    order_schema = [OrderReportSchema.model_validate(report) for report in report_results]
    return order_schema


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
