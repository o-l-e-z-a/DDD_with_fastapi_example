from src.domain.base.values import CountNumber, Name, PositiveIntNumber
from src.domain.orders.entities import Order, OrderingProcess, Promotion, TotalAmount, TotalAmountResult
from src.domain.schedules.values import SlotTime
from src.domain.users.entities import User
from src.logic.dto.order_dto import OrderCreateDTO, OrderUpdateDTO, PromotionAddDTO, PromotionUpdateDTO, TotalAmountDTO
from src.logic.exceptions.order_exceptions import OrderNotFoundLogicException, PromotionNotFoundLogicException, \
    NotUserOrderLogicException
from src.logic.exceptions.schedule_exceptions import ScheduleNotFoundLogicException, ServiceNotFoundLogicException
from src.logic.exceptions.user_exceptions import UserPointNotFoundLogicException
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
                raise UserPointNotFoundLogicException(id=user_id)
            schedule = await self.uow.schedules.find_one_or_none(id=total_amount_dto.schedule_id)
            if not schedule:
                raise ScheduleNotFoundLogicException(id=total_amount_dto.schedule_id)
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
            promotion = await self.uow.promotions.find_one_or_none(code=order_data.total_amount.promotion_code)
            user_point = await self.uow.user_points.find_one_or_none(user_id=user.id)
            if not user_point:
                raise UserPointNotFoundLogicException(id=user.id)
            schedule = await self.uow.schedules.find_one_with_consumables(id=order_data.total_amount.schedule_id)
            if not schedule:
                raise ScheduleNotFoundLogicException(id=order_data.total_amount.schedule_id)
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
                raise OrderNotFoundLogicException(id=order_data.order_id)
            elif not order.user == user:
                raise NotUserOrderLogicException()
            occupied_slots = await self.uow.slots.find_all(day=order.slot.schedule.day)
            ordering_process = OrderingProcess()
            ordering_process.update_slot_time(
                order, time_start=SlotTime(order_data.time_start), occupied_slots=occupied_slots
            )
            await self.uow.slots.update(order.slot)
            await self.uow.commit()
            return await self.uow.orders.find_one_or_none(id=order.id)

    async def update_order_photos(self, order_id: int, photo_before, photo_after):
        async with self.uow:
            order = await self.uow.orders.find_one_or_none(id=order_id)
            if not order:
                raise OrderNotFoundLogicException(id=order_id)
            order = await self.uow.orders.update_photo(
                order=order,
                photo_before=photo_before,
                photo_after=photo_after,
            )
            await self.uow.commit()
            return await self.uow.orders.find_one_or_none(id=order.id)

    async def delete_order(self, order_id: int, user: User):
        async with self.uow:
            order = await self.uow.orders.find_one_or_none(id=order_id)
            if not order:
                raise OrderNotFoundLogicException(id=order_id)
            elif not order.user == user:
                raise NotUserOrderLogicException()
            user_point = await self.uow.user_points.find_one_or_none(user_id=user.id)
            if not user_point:
                raise UserPointNotFoundLogicException(id=user.id)
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

    async def get_service_report(self) -> dict[str, int | str]:
        async with self.uow:
            orders = await self.uow.orders.get_order_report_by_service()
        return orders


class PromotionService:
    def __init__(self, uow: SQLAlchemyOrderUnitOfWork):
        self.uow = uow

    async def get_promotions(self) -> list[Promotion]:
        async with self.uow:
            inventories = await self.uow.promotions.find_all()
        return inventories

    async def add_promotion(self, promotion_data: PromotionAddDTO) -> Promotion:
        async with self.uow:
            services = await self.uow.services.get_services_by_ids(promotion_data.services_id)
            if not services:
                raise ServiceNotFoundLogicException(id=promotion_data.services_id)
            promotion = Promotion(
                code=Name(promotion_data.code),
                sale=PositiveIntNumber(promotion_data.sale),
                is_active=promotion_data.is_active,
                day_start=promotion_data.day_start,
                day_end=promotion_data.day_end,
                services=services,
            )
            promotion_from_repo = await self.uow.promotions.add(entity=promotion)
            await self.uow.commit()
            return await self.uow.promotions.find_one_or_none(id=promotion_from_repo.id)

    async def update_promotion(self, promotion_data: PromotionUpdateDTO) -> Promotion:
        async with self.uow:
            promotion = await self.uow.promotions.find_one_or_none(id=promotion_data.promotion_id)
            if not promotion:
                raise PromotionNotFoundLogicException(id=promotion_data.promotion_id)
            services = await self.uow.services.get_services_by_ids(promotion_data.services_id)
            if not services:
                raise ServiceNotFoundLogicException(id=promotion_data.services_id)
            promotion.code = Name(promotion_data.code)
            promotion.sale = PositiveIntNumber(promotion_data.sale)
            promotion.is_active = promotion_data.is_active
            promotion.day_start = promotion_data.day_start
            promotion.day_end = promotion_data.day_end
            promotion.services = services
            promotion_from_repo = await self.uow.promotions.update(entity=promotion)
            await self.uow.commit()
            return await self.uow.promotions.find_one_or_none(id=promotion_from_repo.id)

    async def delete_promotion(self, promotion_id: int):
        async with self.uow:
            promotion = await self.uow.promotions.find_one_or_none(id=promotion_id)
            if not promotion:
                raise PromotionNotFoundLogicException(id=promotion_id)
            await self.uow.promotions.delete(id=promotion_id)
            await self.uow.commit()
