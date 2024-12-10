from dataclasses import asdict

from fastapi import APIRouter, status, Depends
from fastapi_cache.decorator import cache

from src.logic.dto.order_dto import OrderCreateDTO, TotalAmountDTO, OrderUpdateDTO, PromotionAddDTO, PromotionUpdateDTO
from src.logic.services.order_service import OrderService, PromotionService
from src.presentation.api.dependencies import get_order_service, CurrentUser, get_promotion_service
from src.presentation.api.orders.schema import AllOrderSchema, OrderSchema, OrderCreateSchema, TotalAmountCreateSchema, \
    TotalAmountSchema, PromotionSchema, PromotionAddSchema, OrderReportSchema
from src.presentation.api.schedules.schema import SlotUpdateSchema

router = APIRouter(
    prefix='/api',
    tags=['order']
)


@router.get("/all_orders/", description='все заказы для просмотра мастером')
@cache(expire=60)
async def get_all_orders(order_service: OrderService = Depends(get_order_service)) -> list[AllOrderSchema]:
    results = await order_service.get_all_orders()
    order_schemas = [AllOrderSchema.model_validate(order.to_dict()) for order in results]
    return order_schemas


@router.post("/total_amount/")
async def get_total_amount(
        total_amount_data: TotalAmountCreateSchema,
        user: CurrentUser,
        order_service: OrderService = Depends(get_order_service)
) -> TotalAmountSchema:
    total_amount = await order_service.get_total_amount(
        total_amount_dto=TotalAmountDTO(**total_amount_data.model_dump()), user=user
    )
    return TotalAmountSchema(**asdict(total_amount))


@router.get("/orders/", description='все заказы клиента')
@cache(expire=60)
async def get_client_orders(user: CurrentUser, order_service: OrderService = Depends(get_order_service)) -> list[OrderSchema]:
    results = await order_service.get_client_orders(user=user)
    order_schemas = [OrderSchema.model_validate(order.to_dict()) for order in results]
    return order_schemas


@router.post("/order/add/", status_code=status.HTTP_201_CREATED)
async def add_order(
        order_data: OrderCreateSchema,
        user: CurrentUser,
        order_service: OrderService = Depends(get_order_service),
) -> OrderSchema:
    order = await order_service.add_order(
        order_data=OrderCreateDTO(
            total_amount=TotalAmountDTO(
                schedule_id=order_data.slot.schedule_id,
                point=order_data.point,
                promotion_code=order_data.promotion_code,
            ),
            time_start=order_data.slot.time_start
        ),
        user=user
    )
    order_schema = OrderSchema.model_validate(order.to_dict())
    # order_create_send_mail_task.delay(order_dict)
    return order_schema


@router.put("/order/{order_id}/update/")
async def update_order(
        order_id: int,
        slot_data: SlotUpdateSchema,
        user: CurrentUser,
        order_service: OrderService = Depends(get_order_service)
) -> OrderSchema:
    order = await order_service.update_order(
        order_data=OrderUpdateDTO(**slot_data.model_dump(), order_id=order_id), user=user
    )
    order_schema = OrderSchema.model_validate(order.to_dict())
    return order_schema


# @router.patch("/order/{order_id}/update_photo/")
# async def update_photo(
#         order_id: int,
#         photo_before: UploadFile,
#         photo_after: UploadFile,
#         order_service: OrderService = Depends(get_order_service)
# ) -> OrderSchema:
#     order = await order_dao.find_one_or_none(id=order_id)
#     if not order:
#         raise OrderNotFound()
#     order = await order_dao.update_photo(
#         order=order,
#         photo_before=photo_before,
#         photo_after=photo_after,
#     )
#     order_schema = OrderSchema.model_validate(order)
#     return order_schema


@router.delete("/order/{order_id}/delete/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: int,
    user: CurrentUser,
    order_service: OrderService = Depends(get_order_service),
):
    await order_service.delete_order(order_id=order_id, user=user)


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
    promotion_data: PromotionAddSchema,
    promotion_service: PromotionService = Depends(get_promotion_service)
) -> PromotionSchema:
    promotion = await promotion_service.add_promotion(promotion_data=PromotionAddDTO(**promotion_data.model_dump()))
    promotion_schema = PromotionSchema.model_validate(promotion.to_dict())
    return promotion_schema


@router.patch("/promotion/{promotion_id}/update/")
async def patch_promotion(
    promotion_id: int,
    promotion_data: PromotionAddSchema,
    promotion_service: PromotionService = Depends(get_promotion_service)
) -> PromotionSchema:
    promotion = await promotion_service.update_promotion(
        promotion_data=PromotionUpdateDTO(**promotion_data.model_dump(), promotion_id=promotion_id)
    )
    promotion_schema = PromotionSchema.model_validate(promotion.to_dict())
    return promotion_schema


@router.delete("/promotion/{promotion_id}/delete/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_promotion(promotion_id: int, promotion_service: PromotionService = Depends(get_promotion_service)):
    await promotion_service.delete_promotion(promotion_id=promotion_id)
