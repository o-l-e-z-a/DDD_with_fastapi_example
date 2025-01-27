from dataclasses import dataclass
from typing import Annotated

from pydantic import Field

from src.domain.base.values import CountNumber
from src.domain.orders.entities import OrderingProcess
from src.domain.schedules.values import SlotTime
from src.domain.users.entities import User
from src.logic.commands.base import BaseCommand, CommandHandler
from src.logic.exceptions.schedule_exceptions import (
    ScheduleNotFoundLogicException,
)
from src.logic.exceptions.user_exceptions import (
    UserPointNotFoundLogicException,
)
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
            if not user_point:
                raise UserPointNotFoundLogicException(id=user.id)
            schedule = await self.uow.schedules.find_one_with_consumables(id=command.total_amount.schedule_id)
            if not schedule:
                raise ScheduleNotFoundLogicException(id=command.total_amount.schedule_id)
            occupied_slots = await self.uow.slots.find_all(day=schedule.day)
            ordering_process = OrderingProcess()
            order_from_aggregate = ordering_process.add(
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
            return order_with_detail_info
