from src.domain.base.values import CountNumber
from src.domain.orders.entities import Promotion, TotalAmountResult, TotalAmountDomainService

from src.domain.users.entities import User
from src.logic.dto.order_dto import (
    TotalAmountDTO,
)
from src.logic.exceptions.schedule_exceptions import ScheduleNotFoundLogicException
from src.logic.exceptions.user_exceptions import UserPointNotFoundLogicException
from src.infrastructure.db.uows.order_uow import SQLAlchemyOrderUnitOfWork


class TotalAmountService:
    def __init__(self, uow: SQLAlchemyOrderUnitOfWork):
        self.uow = uow

    async def get_total_amount(self, total_amount_dto: TotalAmountDTO, user: User) -> TotalAmountResult:
        user_id = user.id
        async with self.uow:
            promotion = await self.uow.promotions.find_one_or_none(code=total_amount_dto.promotion_code)
            user_point = await self.uow.user_points.find_one_or_none(user_id=user_id)
            if not user_point:
                raise UserPointNotFoundLogicException(id=user_id)
            schedule = await self.uow.schedules.find_one_or_none(id=total_amount_dto.schedule_id)
            if not schedule:
                raise ScheduleNotFoundLogicException(id=total_amount_dto.schedule_id)
            amount_result = TotalAmountDomainService().calculate(
                promotion=promotion,
                service=service,
                user_point=user_point,
                input_user_point=CountNumber(total_amount_dto.point),
            )
            return amount_result


class PromotionService:
    def __init__(self, uow: SQLAlchemyOrderUnitOfWork):
        self.uow = uow

    async def get_promotions(self) -> list[Promotion]:
        async with self.uow:
            inventories = await self.uow.promotions.find_all()
        return inventories
