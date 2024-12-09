from dataclasses import dataclass, field
from datetime import date, datetime

from src.domain.base.entities import BaseEntity
from src.domain.base.values import CountNumber, Name, PositiveIntNumber
from src.domain.orders.values import LESS_POINT_WARNINGS, MINIMUM_BALANCE, MORE_POINT_WARNINGS
from src.domain.schedules.entities import Schedule, Service, Slot, SlotsForSchedule
from src.domain.schedules.exceptions import SlotOccupiedException
from src.domain.schedules.values import SlotTime
from src.domain.users.entities import User, UserPoint


@dataclass()
class Promotion(BaseEntity):
    code: Name
    sale: PositiveIntNumber
    is_active: bool
    day_start: date
    day_end: date
    services: list[Service] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'code': self.code.as_generic_type(),
            'sale': self.sale.as_generic_type(),
            'is_active': self.is_active,
            'day_start': self.day_start,
            'day_end': self.day_end,
            'services': [service.to_dict() for service in self.services]
        }


@dataclass()
class Order(BaseEntity):
    user: User
    slot: Slot
    point_uses: CountNumber
    promotion_sale: CountNumber
    total_amount: PositiveIntNumber
    date_add: date = datetime.today()

    def to_dict(self) -> dict:
        user = self.user.to_dict() if self.user else None
        slot = self.slot.to_dict() if self.slot else None
        return {
            'id': self.id,
            'point_uses': self.point_uses.as_generic_type(),
            'promotion_sale': self.promotion_sale.as_generic_type(),
            'total_amount': self.total_amount.as_generic_type(),
            'date_add': self.date_add,
            'user': user,
            'slot': slot
        }


@dataclass()
class TotalAmountResult:
    total_amount: int
    point_uses: int
    promotion_sale: int
    warnings: list[str] = field(default_factory=list)


class TotalAmount:
    def __init__(
        self, promotion: Promotion | None, user_point: UserPoint, schedule: Schedule, input_user_point: CountNumber
    ):
        self.promotion = promotion
        self.schedule = schedule
        self.user_point = user_point
        self.input_user_point = input_user_point

    def calculate(self) -> TotalAmountResult:
        service = self.schedule.service
        total_amount = service.price.as_generic_type()
        point = self.input_user_point.as_generic_type()
        warnings = []
        promotion_sale = 0

        if self.promotion:
            promotion_sale = int(service.price * self.promotion.sale / 100)
            total_amount -= promotion_sale
        if self.user_point.count < point:
            point = 0
            warnings.append(LESS_POINT_WARNINGS)
        elif point >= total_amount:
            point = total_amount - MINIMUM_BALANCE
            total_amount = MINIMUM_BALANCE
            warnings.append(MORE_POINT_WARNINGS)
        elif 1 < total_amount - point < MINIMUM_BALANCE:
            diff = point - MINIMUM_BALANCE
            point -= diff
            total_amount -= point
        else:
            total_amount -= point

        return TotalAmountResult(
            total_amount=total_amount, point_uses=point, promotion_sale=promotion_sale, warnings=warnings
        )


class OrderingProcess:
    def update_slot_time(
        self,
        order: Order,
        time_start: SlotTime,
        occupied_slots: list[Slot]
    ):
        slot_for_schedule = SlotsForSchedule()
        if not slot_for_schedule.check_slot_time_is_free(slot_time=time_start, occupied_slots=occupied_slots):
            raise SlotOccupiedException()
        order.slot.time_start = time_start

    def add(
        self,
        promotion: Promotion | None,
        user_point: UserPoint,
        schedule: Schedule,
        input_user_point: CountNumber,
        user: User,
        time_start: SlotTime,
        occupied_slots: list[Slot],
    ) -> Order:
        slot_for_schedule = SlotsForSchedule()
        if not slot_for_schedule.check_slot_time_is_free(slot_time=time_start, occupied_slots=occupied_slots):
            raise SlotOccupiedException()

        slot = Slot(schedule=schedule, time_start=time_start)
        total_amount = TotalAmount(
            promotion=promotion,
            user_point=user_point,
            schedule=schedule,
            input_user_point=input_user_point,
        )

        total_amount_result = total_amount.calculate()

        order = Order(
            user=user,
            slot=slot,
            point_uses=CountNumber(total_amount_result.point_uses),
            promotion_sale=CountNumber(total_amount_result.promotion_sale),
            total_amount=PositiveIntNumber(total_amount_result.total_amount),
        )

        self._decrease_user_point(user_point, CountNumber(total_amount_result.point_uses))
        self._decrease_service_inventory_count(order)

        return order

    def cancel(self, order: Order, user_point: UserPoint):
        self._increase_user_point(user_point, order.point_uses)
        self._increase_service_inventory_count(order)

    def _decrease_user_point(self, user_point: UserPoint, point_uses: CountNumber) -> None:
        # move to user_point class ?
        user_point.count = CountNumber(user_point.count - point_uses)

    def _decrease_service_inventory_count(self, order: Order) -> None:
        # move to order class ?
        service = order.slot.schedule.service
        for consumable in service.consumables:
            consumable.inventory.stock_count = CountNumber(consumable.inventory.stock_count - consumable.count)

    def _increase_user_point(self, user_point: UserPoint, point_uses: CountNumber) -> None:
        user_point.count = CountNumber(user_point.count + point_uses)

    def _increase_service_inventory_count(self, order: Order) -> None:
        service = order.slot.schedule.service
        for consumable in service.consumables:
            consumable.inventory.stock_count = CountNumber(consumable.inventory.stock_count + consumable.count)
