from dataclasses import asdict

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from starlette import status

from src.domain.orders.entities import Promotion
from src.domain.orders.exceptions import OrderIsPayedException
from src.infrastructure.db.exceptions import InsertException
from src.logic.commands.order_commands import (
    AddPromotionCommand,
    CalculateOrderCommand,
    DeletePromotionCommand,
    OrderPayCommand,
    UpdatePromotionCommand,
)
from src.logic.dto.order_dto import PromotionDetailDTO
from src.logic.exceptions.base_exception import NotFoundLogicException
from src.logic.mediator.base import Mediator
from src.logic.queries.order_queries import GetAllPromotionsQuery, OrderPaymentDetailQuery, UserPointQuery
from src.presentation.api.exceptions import (
    NotCorrectDataHTTPException,
    NotFoundHTTPException,
    OrderPaymentNotCorrectStatusException,
)
from src.presentation.api.orders.schema import (
    OrderPaymentDetailSchema,
    OrderPaymentSchema,
    PromotionAddSchema,
    PromotionDetailSchema,
    PromotionSchema,
    TotalAmountInputSchema,
    TotalAmountSchema,
    UserPointSchema,
)
from src.presentation.api.users.utils import CurrentUser

router = APIRouter(route_class=DishkaRoute, prefix="/api", tags=["order"])


@router.get("/user_point/")
async def get_user_point(user: FromDishka[CurrentUser], mediator: FromDishka[Mediator]) -> UserPointSchema:
    try:
        user_point = await mediator.handle_query(UserPointQuery(user_id=user.id))
    except NotFoundLogicException as err:
        raise NotFoundHTTPException(detail=err.title)
    user_point_schema = UserPointSchema.model_validate(user_point)
    return user_point_schema


@router.get("/promotions/")
async def get_promotions(
    mediator: FromDishka[Mediator],
) -> list[PromotionDetailSchema]:
    results: list[PromotionDetailDTO] = await mediator.handle_query(GetAllPromotionsQuery())
    promotion_schemas = [PromotionDetailSchema.model_validate(promotion) for promotion in results]
    return promotion_schemas


@router.get("/order_payment/{order_pk}/detail")
async def get_order_payment_detail(
    order_pk: int,
    mediator: FromDishka[Mediator],
) -> OrderPaymentDetailSchema:
    try:
        result: list[PromotionDetailDTO] = await mediator.handle_query(OrderPaymentDetailQuery(order_id=order_pk))
    except NotFoundLogicException as err:
        raise NotFoundHTTPException(detail=err.title)
    result_schema = OrderPaymentDetailSchema.model_validate(result)
    return result_schema


@router.post("/order_payment/{order_payment_pk}/calculate")
async def calculate_total_amount(
    order_payment_pk: int,
    total_amount_data: TotalAmountInputSchema,
    user: FromDishka[CurrentUser],
    mediator: FromDishka[Mediator],
) -> TotalAmountSchema:
    try:
        total_amount = (
            await mediator.handle_command(
                CalculateOrderCommand(
                    user_id=user.id, order_payment_id=order_payment_pk, **total_amount_data.model_dump()
                )
            )
        )[0]
    except NotFoundLogicException as err:
        raise NotFoundHTTPException(detail=err.title)
    return TotalAmountSchema(**asdict(total_amount))


@router.post("/order_payment/{order_payment_pk}/pay")
async def order_pay(
    order_payment_pk: int,
    total_amount_data: TotalAmountInputSchema,
    user: FromDishka[CurrentUser],
    mediator: FromDishka[Mediator],
) -> OrderPaymentSchema:
    try:
        order_payment = (
            await mediator.handle_command(
                OrderPayCommand(user_id=user.id, order_payment_id=order_payment_pk, **total_amount_data.model_dump())
            )
        )[0]
    except NotFoundLogicException as err:
        raise NotFoundHTTPException(detail=err.title)
    except OrderIsPayedException as err:
        raise OrderPaymentNotCorrectStatusException(detail=err.title)
    order_payment_schema = OrderPaymentSchema.model_validate(order_payment.to_dict())
    return order_payment_schema


@router.post("/promotion/add/", status_code=status.HTTP_201_CREATED)
async def add_promotion(
    promotion_data: PromotionAddSchema,
    # admin: FromDishka[CurrentAdmin],
    mediator: FromDishka[Mediator],
) -> PromotionSchema:
    try:
        promotion: Promotion = (
            await mediator.handle_command(AddPromotionCommand(**promotion_data.model_dump(exclude_unset=True)))
        )[0]
    except NotFoundLogicException as err:
        raise NotFoundHTTPException(detail=err.title)
    except InsertException as err:
        raise NotCorrectDataHTTPException(detail=err.title)
    promotion_schema = PromotionSchema.model_validate(promotion.to_dict())
    return promotion_schema


@router.patch("/promotion/{promotion_pk}/update/")
async def patch_promotion(
    promotion_pk: int,
    promotion_data: PromotionAddSchema,
    # admin: FromDishka[CurrentAdmin],
    mediator: FromDishka[Mediator],
) -> PromotionSchema:
    try:
        promotion: Promotion = (
            await mediator.handle_command(
                UpdatePromotionCommand(**promotion_data.model_dump(), promotion_id=promotion_pk)
            )
        )[0]
    except NotFoundLogicException as err:
        raise NotFoundHTTPException(detail=err.title)
    except InsertException as err:
        raise NotCorrectDataHTTPException(detail=err.title)
    promotion_schema = PromotionSchema.model_validate(promotion.to_dict())
    return promotion_schema


@router.delete("/promotion/{promotion_pk}/delete/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_promotion(
    promotion_pk: int,
    # admin: FromDishka[CurrentAdmin],
    mediator: FromDishka[Mediator],
):
    try:
        await mediator.handle_command(DeletePromotionCommand(promotion_id=promotion_pk))
    except NotFoundLogicException as err:
        raise NotFoundHTTPException(detail=err.title)
