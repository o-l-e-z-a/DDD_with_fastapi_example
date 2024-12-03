from src.domain.base.values import CountNumber
from src.domain.orders.entities import Order, TotalAmount, TotalAmountResult, OrderingProcess
from src.domain.schedules.values import SlotTime
from src.domain.users.entities import User
from src.logic.dto.order_dto import TotalAmountDTO, OrderCreateDTO
from src.logic.uows.order_uow import SQLAlchemyOrderUnitOfWork


class OrderService:
    def __init__(self, uow: SQLAlchemyOrderUnitOfWork):
        self.uow = uow

    async def get_all_orders(self) -> list[Order]:
        async with self.uow:
            orders = await self.uow.orders.find_all()
        return orders

    async def get_total_amount(self, total_amount_dto: TotalAmountDTO, user: User) -> TotalAmountResult:
        user_id = user.id
        async with self.uow:
            promotion = await self.uow.promotions.find_one_or_none(code=total_amount_dto.promotion_code)
            user_point = await self.uow.user_points.find_one_or_none(user_id=user_id)
            if not user_point:
                raise Exception
            schedule = await self.uow.schedules.find_one_or_none(id=total_amount_dto.schedule_id)
            if not schedule:
                raise Exception
            amount_result = TotalAmount(
                promotion=promotion,
                schedule=schedule,
                user_point=user_point,
                input_user_point=CountNumber(total_amount_dto.point),
            ).calculate()
            return amount_result

    async def get_client_orders(self, user: User) -> list[Order]:
        async with self.uow:
            orders = await self.uow.orders.find_all(user_id=user.id)
        return orders

    async def add_order(self, order_data: OrderCreateDTO, user: User):
        async with self.uow:
            if not user:
                raise Exception
            promotion = await self.uow.promotions.find_one_or_none(code=order_data.total_amount.promotion_code)
            user_point = await self.uow.user_points.find_one_or_none(user_id=user.id)
            if not user_point:
                raise Exception
            schedule = await self.uow.schedules.find_one_or_none(id=order_data.total_amount.schedule_id)
            if not schedule:
                raise Exception
            occupied_slots = await self.uow.slots.find_all(day=schedule.day)
            ordering_process = OrderingProcess()
            order = ordering_process.add(
                promotion=promotion,
                user_point=user_point,
                schedule=schedule,
                input_user_point=CountNumber(order_data.total_amount.point),
                user=user,
                time_start=SlotTime(order_data.time_start),
                occupied_slots=occupied_slots,
            )
            slot_from_repo = await self.uow.slots.add(order.slot)
            order.slot = slot_from_repo
            order_from_repo = await self.uow.orders.add(order)
            await self.uow.commit()
            return await self.uow.orders.find_one_or_none(id=order_from_repo.id)
