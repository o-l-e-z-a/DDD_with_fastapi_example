from src.domain.base.values import CountNumber
from src.domain.orders.entities import Order, TotalAmount, TotalAmountResult, OrderingProcess, Promotion
from src.domain.schedules.values import SlotTime
from src.domain.users.entities import User
from src.logic.dto.order_dto import TotalAmountDTO, OrderCreateDTO, OrderUpdateDTO, PromotionAddDTO, PromotionUpdateADTO
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

    async def add_order(self, order_data: OrderCreateDTO, user: User) -> Order:
        async with self.uow:
            if not user:
                raise Exception
            promotion = await self.uow.promotions.find_one_or_none(code=order_data.total_amount.promotion_code)
            user_point = await self.uow.user_points.find_one_or_none(user_id=user.id)
            if not user_point:
                raise Exception
            schedule = await self.uow.schedules.find_one_with_consumables(id=order_data.total_amount.schedule_id)
            if not schedule:
                raise Exception
            occupied_slots = await self.uow.slots.find_all(day=schedule.day)
            ordering_process = OrderingProcess()
            order_from_aggregate = ordering_process.add(
                promotion=promotion,
                user_point=user_point,
                schedule=schedule,
                input_user_point=CountNumber(order_data.total_amount.point),
                user=user,
                time_start=SlotTime(order_data.time_start),
                occupied_slots=occupied_slots,
            )
            slot_from_repo = await self.uow.slots.add(order_from_aggregate.slot)
            order_from_aggregate.slot.id = slot_from_repo.id
            order_from_repo = await self.uow.orders.add(order_from_aggregate)
            order_with_detail_info = await self.uow.orders.find_one_or_none(id=order_from_repo.id)
            await self.uow.user_points.update(user_point)
            service_with_consumables = await self.uow.services.get_service_with_consumable(
                service_id=order_with_detail_info.slot.schedule.service.id
            )
            for consumable in service_with_consumables.consumables:
                for consumable_from_aggregate in order_from_aggregate.slot.schedule.service.consumables:
                    if consumable.id == consumable_from_aggregate.id:
                        await self.uow.inventories.update(consumable_from_aggregate.inventory)
            await self.uow.commit()
            return order_with_detail_info

    async def update_order(self, order_data: OrderUpdateDTO, user: User) -> Order:
        async with self.uow:
            order = await self.uow.orders.find_one_or_none(id=order_data.order_id)
            if not order:
                raise Exception
            elif not order.user == user:
                raise Exception
            occupied_slots = await self.uow.slots.find_all(day=order.slot.schedule.day)
            ordering_process = OrderingProcess()
            ordering_process.update_slot_time(
                order, time_start=SlotTime(order_data.time_start), occupied_slots=occupied_slots
            )
            order_from_repo = await self.uow.slots.update(order.slot)
            await self.uow.commit()
            return await self.uow.orders.find_one_or_none(id=order_from_repo.id)

    async def delete_order(self, order_id: int, user: User):
        async with self.uow:
            if not user:
                raise Exception
            user_point = await self.uow.user_points.find_one_or_none(user_id=user.id)
            if not user_point:
                raise Exception
            order = await self.uow.orders.find_one_or_none(id=order_id)
            if not order:
                raise Exception
            elif not order.user == user:
                raise Exception
            schedule = await self.uow.schedules.find_one_with_consumables(id=order.slot.schedule.id)
            order.slot.schedule = schedule
            ordering_process = OrderingProcess()
            ordering_process.cancel(order=order, user_point=user_point)
            await self.uow.user_points.update(user_point)
            service_with_consumables = await self.uow.services.get_service_with_consumable(
                service_id=order.slot.schedule.service.id
            )
            for consumable in service_with_consumables.consumables:
                for consumable_from_aggregate in order.slot.schedule.service.consumables:
                    if consumable.id == consumable_from_aggregate.id:
                        await self.uow.inventories.update(consumable_from_aggregate.inventory)
            await self.uow.slots.delete(id=order.slot.id)
            await self.uow.commit()

    async def get_service_report(self):
        pass


class PromotionService:
    def __init__(self, uow: SQLAlchemyOrderUnitOfWork):
        self.uow = uow

    async def get_promotions(self) -> list[Promotion]:
        pass

    async def add_promotion(
        self,
        promotion_data: PromotionAddDTO
    ) -> Promotion:
        pass

    async def update_promotion(
        self,
        promotion_data: PromotionUpdateADTO
    ) -> Promotion:
        pass

    async def delete_promotion(self, promotion_id: int):
        pass
