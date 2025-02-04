from dataclasses import dataclass
from datetime import date
from typing import Annotated

from pydantic import Field, PositiveInt

from src.domain.base.values import CountNumber, Name, PositiveIntNumber
from src.domain.orders.entities import Order, Promotion
from src.domain.schedules.values import SlotTime
from src.domain.users.entities import User
from src.logic.commands.base import BaseCommand, CommandHandler
from src.logic.dto.order_dto import PhotoDTO
from src.logic.exceptions.order_exceptions import NotUserOrderLogicException, OrderNotFoundLogicException
from src.logic.exceptions.schedule_exceptions import ScheduleNotFoundLogicException, ServiceNotFoundLogicException
from src.logic.exceptions.user_exceptions import UserPointNotFoundLogicException
from src.logic.uows.order_uow import SQLAlchemyOrderUnitOfWork

int_ge_0 = Annotated[int, Field(ge=0)]
slot_type = Annotated[str, Field(pattern=r"^(?:[01][0-9]|2?[0-3]):[0-5]\d$")]


class TotalAmountDTO(BaseCommand):
    schedule_id: int
    point: int_ge_0 | None = 0
    promotion_code: str | None = "0"


class AddOrderCommand(BaseCommand):
    total_amount: TotalAmountDTO
    time_start: slot_type
    user: User


@dataclass(frozen=True)
class AddOrderCommandCommandHandler(CommandHandler[AddOrderCommand, None]):
    uow: SQLAlchemyOrderUnitOfWork

    async def handle(self, command: AddOrderCommand) -> None:
        async with self.uow:
            user = command.user
            promotion = await self.uow.promotions.find_one_or_none(code=command.total_amount.promotion_code)
            user_point = await self.uow.user_points.find_one_or_none(user_id=user.id)
            service = await self.uow.services.find_one_or_none(id=command.service_id)
            if not service:
                raise ServiceNotFoundLogicException(id=command.service_id)
            if not user_point:
                raise UserPointNotFoundLogicException(id=user.id)
            schedule = await self.uow.schedules.find_one_with_consumables(id=command.total_amount.schedule_id)
            if not schedule:
                raise ScheduleNotFoundLogicException(id=command.total_amount.schedule_id)
            occupied_slots = await self.uow.slots.find_all(day=schedule.day)
            order_from_aggregate = Order.add(
                promotion=promotion,
                user_point=user_point,
                schedule=schedule,
                input_user_point=CountNumber(command.total_amount.point),
                user=user,
                time_start=SlotTime(command.time_start),
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
            events = order_from_aggregate.pull_events()
            print("events", events)
            await self.mediator.publish(events)
            return order_with_detail_info


class UpdateOrderCommand(BaseCommand):
    order_id: PositiveInt
    time_start: slot_type
    user: User


@dataclass(frozen=True)
class UpdateOrderCommandCommandHandler(CommandHandler[UpdateOrderCommand, None]):
    uow: SQLAlchemyOrderUnitOfWork

    async def handle(self, command: UpdateOrderCommand) -> None:
        async with self.uow:
            order = await self.uow.orders.find_one_or_none(id=command.order_id)
            if not order:
                raise OrderNotFoundLogicException(id=command.order_id)
            elif not order.user == command.user:
                raise NotUserOrderLogicException()
            occupied_slots = await self.uow.slots.find_all(day=order.slot.schedule.day)
            order.update_slot_time(time_start=SlotTime(command.time_start), occupied_slots=occupied_slots)
            await self.uow.slots.update(order.slot)
            await self.uow.commit()
            return await self.uow.orders.find_one_or_none(id=order.id)


class UpdatePhotoOrderCommand(BaseCommand):
    order_id: PositiveInt
    photo_before: PhotoDTO
    photo_after: PhotoDTO


@dataclass(frozen=True)
class UpdatePhotoOrderCommandCommandHandler(CommandHandler[UpdatePhotoOrderCommand, None]):
    uow: SQLAlchemyOrderUnitOfWork

    async def handle(self, command: UpdatePhotoOrderCommand) -> None:
        async with self.uow:
            order = await self.uow.orders.find_one_or_none(id=command.order_id)
            if not order:
                raise OrderNotFoundLogicException(id=command.order_id)
            order_from_repo = await self.uow.orders.update_photo(
                entity=order,
                photo_before=command.photo_before,
                photo_after=command.photo_after,
            )
            await self.uow.commit()
            return await self.uow.orders.find_one_or_none(id=order_from_repo.id)


class DeleteOrderCommand(BaseCommand):
    order_id: PositiveInt
    user: User


@dataclass(frozen=True)
class DeleteOrderCommandCommandHandler(CommandHandler[DeleteOrderCommand, None]):
    uow: SQLAlchemyOrderUnitOfWork

    async def handle(self, command: DeleteOrderCommand) -> None:
        async with self.uow:
            order = await self.uow.orders.find_one_or_none(id=command.order_id)
            if not order:
                raise OrderNotFoundLogicException(id=command.order_id)
            elif not order.user == command.user:
                raise NotUserOrderLogicException()

            user_point = await self.uow.user_points.find_one_or_none(user_id=command.user.id)
            if not user_point:
                raise UserPointNotFoundLogicException(id=command.user.id)
            order.cancel(user_point=user_point)
            await self.uow.user_points.update(user_point)

            # schedule = await self.uow.schedules.find_one_with_consumables(id=order.slot.schedule.id)
            # order.slot.schedule = schedule
            # service_with_consumables = await self.uow.services.get_service_with_consumable(
            #     service_id=order.slot.schedule.service.id
            # )
            # for consumable in service_with_consumables.consumables:
            #     for consumable_from_aggregate in order.slot.schedule.service.consumables:
            #         if consumable.id == consumable_from_aggregate.id:
            #             await self.uow.inventories.update(consumable_from_aggregate.inventory)

            await self.uow.slots.delete(id=order.slot.id)
            await self.uow.commit()


class AddPromotionCommand(BaseCommand):
    code: str = Field(..., max_length=15)
    sale: int = Field(..., ge=0, lt=100)
    is_active: bool = True
    day_start: date
    day_end: date
    services_id: list[int]


@dataclass(frozen=True)
class AddPromotionCommandCommandHandler(CommandHandler[AddPromotionCommand, None]):
    uow: SQLAlchemyOrderUnitOfWork

    async def handle(self, command: AddPromotionCommand) -> None:
        async with self.uow:
            services = await self.uow.services.get_services_by_ids(command.promotion_data.services_id)
            if not services:
                raise ServiceNotFoundLogicException(id=command.promotion_data.services_id)
            promotion = Promotion(
                code=Name(command.promotion_data.code),
                sale=PositiveIntNumber(command.promotion_data.sale),
                is_active=command.promotion_data.is_active,
                day_start=command.promotion_data.day_start,
                day_end=command.promotion_data.day_end,
                services=services,
            )
            promotion_from_repo = await self.uow.promotions.add(entity=promotion)
            await self.uow.commit()
            return await self.uow.promotions.find_one_or_none(id=promotion_from_repo.id)


class UpdatePromotionCommand(AddPromotionCommand):
    promotion_id: PositiveInt


@dataclass(frozen=True)
class UpdatePromotionCommandCommandHandler(CommandHandler[UpdatePromotionCommand, None]):
    uow: SQLAlchemyOrderUnitOfWork

    async def handle(self, command: UpdatePromotionCommand) -> None:
        async with self.uow:
            services = await self.uow.services.get_services_by_ids(command.promotion_data.services_id)
            if not services:
                raise ServiceNotFoundLogicException(id=command.promotion_data.services_id)
            promotion = Promotion(
                code=Name(command.promotion_data.code),
                sale=PositiveIntNumber(command.promotion_data.sale),
                is_active=command.promotion_data.is_active,
                day_start=command.promotion_data.day_start,
                day_end=command.promotion_data.day_end,
                services=services,
            )
            promotion_from_repo = await self.uow.promotions.add(entity=promotion)
            await self.uow.commit()
            return await self.uow.promotions.find_one_or_none(id=promotion_from_repo.id)


class DeletePromotionCommand(BaseCommand):
    promotion_id: PositiveInt


@dataclass(frozen=True)
class DeletePromotionCommandCommandHandler(CommandHandler[DeletePromotionCommand, None]):
    uow: SQLAlchemyOrderUnitOfWork

    async def handle(self, command: DeletePromotionCommand) -> None:
        async with self.uow:
            services = await self.uow.services.get_services_by_ids(command.promotion_data.services_id)
            if not services:
                raise ServiceNotFoundLogicException(id=command.promotion_data.services_id)
            promotion = Promotion(
                code=Name(command.promotion_data.code),
                sale=PositiveIntNumber(command.promotion_data.sale),
                is_active=command.promotion_data.is_active,
                day_start=command.promotion_data.day_start,
                day_end=command.promotion_data.day_end,
                services=services,
            )
            promotion_from_repo = await self.uow.promotions.add(entity=promotion)
            await self.uow.commit()
            return await self.uow.promotions.find_one_or_none(id=promotion_from_repo.id)
