from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

router = APIRouter(route_class=DishkaRoute, prefix="/api", tags=["order"])


# @router.post("/total_amount/")
# async def get_total_amount(
#     total_amount_data: TotalAmountCreateSchema,
#     user: CurrentUser,
#     order_service: OrderService = Depends(get_order_service),
# ) -> TotalAmountSchema:
#     try:
#         total_amount = await order_service.get_total_amount(
#             total_amount_dto=TotalAmountDTO(**total_amount_data.model_dump()), user=user
#         )
#     except NotFoundLogicException as err:
#         raise NotFoundHTTPException(detail=err.title)
#     return TotalAmountSchema(**asdict(total_amount))
#
#
# @router.get("/promotions/")
# async def get_promotions(
# promotion_service: PromotionService = Depends(get_promotion_service)
# ) -> list[PromotionSchema]:
#     results = await promotion_service.get_promotions()
#     promotion_schemas = [PromotionSchema.model_validate(promotion.to_dict()) for promotion in results]
#     return promotion_schemas


# @router.get("/user_point/")
# async def get_user_point(user: CurrentUser, user_service: UserService = Depends(get_user_service)) -> UserPointSchema:
#     try:
#         user_point = await user_service.get_user_point(user=user)
#     except NotFoundLogicException as err:
#         raise NotFoundHTTPException(detail=err.title)
#     user_point_schema = UserPointSchema.model_validate(user_point.to_dict())
#     return user_point_schema


# @router.post("/promotion/add/", status_code=status.HTTP_201_CREATED)
# async def add_promotion(
#     promotion_data: PromotionAddSchema,
#     # admin: CurrentAdmin,
#     mediator: FromDishka[Mediator],
# ) -> PromotionSchema:
#     try:
#         promotion: Promotion = (
#             await mediator.handle_command(AddPromotionCommand(**promotion_data.model_dump(exclude_unset=True)))
#         )[0]
#     except NotFoundLogicException as err:
#         raise NotFoundHTTPException(detail=err.title)
#     promotion_schema = PromotionSchema.model_validate(promotion.to_dict())
#     return promotion_schema
#
#
# @router.patch("/promotion/{promotion_id}/update/")
# async def patch_promotion(
#     promotion_id: int,
#     promotion_data: PromotionAddSchema,
#     # admin: CurrentAdmin,
#     mediator: FromDishka[Mediator],
# ) -> PromotionSchema:
#     try:
#         promotion: Promotion = (
#             await mediator.handle_command(
#                 UpdatePromotionCommand(**promotion_data.model_dump(), promotion_id=promotion_id)
#             )
#         )[0]
#     except NotFoundLogicException as err:
#         raise NotFoundHTTPException(detail=err.title)
#     promotion_schema = PromotionSchema.model_validate(promotion.to_dict())
#     return promotion_schema
#
#
# @router.delete("/promotion/{promotion_id}/delete/", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_promotion(
#     promotion_id: int,
#     # admin: CurrentAdmin,
#     mediator: FromDishka[Mediator],
# ):
#     try:
#         await mediator.handle_command(DeletePromotionCommand(promotion_id=promotion_id))
#     except NotFoundLogicException as err:
#         raise NotFoundHTTPException(detail=err.title)
