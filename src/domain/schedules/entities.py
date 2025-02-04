from __future__ import annotations

import enum

from dataclasses import dataclass, field
from datetime import date, datetime

from src.domain.base.entities import BaseEntity
from src.domain.base.values import Name, PositiveIntNumber
from src.domain.orders.events import OrderCreatedEvent
from src.domain.schedules.exceptions import SlotOccupiedException
from src.domain.schedules.values import END_HOUR, SLOT_DELTA, START_HOUR, SlotTime
from src.domain.users.entities import User

# @dataclass()
# class Inventory(BaseEntity):
#     name: Name
#     unit: Name
#     stock_count: CountNumber
#
#     def to_dict(self) -> dict:
#         return {
#             'id': self.id,
#             'name': self.name.as_generic_type(),
#             'unit': self.unit.as_generic_type(),
#             'stock_count': self.stock_count.as_generic_type(),
#         }
#
#
# @dataclass()
# class Consumable(BaseEntity):
#     inventory: Inventory
#     count: PositiveIntNumber
#
#     def to_dict(self) -> dict:
#         inventory = self.inventory.to_dict() if self.inventory else None
#         return {
#             'id': self.id,
#             'count': self.count.as_generic_type(),
#             'inventory': inventory
#         }


@dataclass()
class Service(BaseEntity):
    name: Name
    description: str
    price: PositiveIntNumber
    # consumables: list[Consumable] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name.as_generic_type(),
            "price": self.price.as_generic_type(),
            "description": self.description,
            # 'consumables': [consumable.to_dict() for consumable in self.consumables]
        }


@dataclass()
class Master(BaseEntity):
    description: str
    user: User
    services_id: list[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        user = self.user.to_dict() if self.user else None
        return {
            "id": self.id,
            "description": self.description,
            "user": user,
            "services_id": [service_id for service_id in self.services_id],
        }


@dataclass()
class Schedule(BaseEntity):
    day: date
    master_id: int
    slots: set[Slot]

    # check schedule by day and master exists

    @classmethod
    def add(cls, day: date, master_id: int):
        all_day_slots = {
            Slot(
                time_start=SlotTime(f"{hour}:00"),
                # schedule_id=se
            )
            for hour in range(START_HOUR, END_HOUR + SLOT_DELTA)
        }

        schedule = cls(day=day, master_id=master_id, slots=all_day_slots)
        return schedule

    #  TODO: check!
    # service in master.services

    def get_free_slots(self, occupied_slots: list[Slot]) -> list[Slot]:
        occupied_slots_time = {occupied_slot for occupied_slot in occupied_slots}
        return sorted(self.slots.difference(occupied_slots_time))

    def to_dict(self) -> dict:
        # master = self.master.to_dict() if self.master else None
        # service = self.service.to_dict() if self.service else None
        return {"id": self.id, "day": self.day, "master_id": self.master_id, "slots": self.slots}


@dataclass()
class Slot(BaseEntity):
    time_start: SlotTime
    # schedule_id: int

    def __eq__(self, other) -> bool:
        return self.time_start == other.time_start

    def __gt__(self, other) -> bool:
        # if self.schedule.day > other.schedule.day:
        #     return True
        # elif self.schedule.day < other.schedule.day:
        #     return False
        # else:
        if self.time_start > other.time_start:
            return True
        return False

    def to_dict(self) -> dict:
        # schedule = self.schedule.to_dict() if self.schedule else None
        return {"id": self.id, "time_start": self.time_start.as_generic_type()}


class SlotsForSchedule:
    def get_free_slots(self, occupied_slots: list[Slot]) -> list[SlotTime]:
        all_day_slots = {SlotTime(f"{hour}:00") for hour in range(START_HOUR, END_HOUR + SLOT_DELTA)}
        occupied_slots_time = {occupied_slot.time_start for occupied_slot in occupied_slots}
        return sorted(all_day_slots.difference(occupied_slots_time))

    def check_slot_time_is_free(self, slot_time: SlotTime, occupied_slots: list[Slot]) -> bool:
        free_slots = self.get_free_slots(occupied_slots)
        return True if slot_time in free_slots else False


class OrderStatus(enum.Enum):
    RECEIVED = enum.auto
    IN_PROGRESS = enum.auto
    FINISHED = enum.auto
    CANCELLED = enum.auto


@dataclass()
class Order(BaseEntity):
    user_id: int
    slot_id: int
    service_id: int
    photo_before_path: str | None = None
    photo_after_path: str | None = None
    date_add: date = datetime.today()
    status: OrderStatus = OrderStatus.RECEIVED

    @classmethod
    def add(cls, user_id: int, service_id: int, slot_id: int, schedule: Schedule, occupied_slots: list[Slot]) -> Order:
        #
        # slot_for_schedule = SlotsForSchedule()
        if slot_id in occupied_slots:
            raise SlotOccupiedException()

        if service_id not in [service.id for service in schedule.master.services]:
            raise

        # slot = Slot(schedule=schedule, time_start=time_start)

        order = cls(
            user_id=user_id,
            service_id=service_id,
            slot_id=slot_id,
        )

        order.register_event(
            OrderCreatedEvent(
                user_id=order.user_id,
                service_id=order.service_id,
                slot_id=order.slot_id,
            )
        )
        return order

    def update_slot_time(self, time_start: SlotTime, occupied_slots: list[Slot]):
        slot_for_schedule = SlotsForSchedule()
        if not slot_for_schedule.check_slot_time_is_free(slot_time=time_start, occupied_slots=occupied_slots):
            raise SlotOccupiedException()
        self.slot.time_start = time_start

    # def cancel(self, user_point: UserPoint):
    #     self._increase_user_point(user_point)

    # self._increase_service_inventory_count()

    # def _decrease_user_point(self, user_point: UserPoint, point_uses: CountNumber) -> None:
    #     # move to user_point class ?
    #     user_point.count = CountNumber(user_point.count - point_uses)
    #
    # def _increase_user_point(self, user_point: UserPoint) -> None:
    #     user_point.count = CountNumber(user_point.count + self.point_uses)

    # def _decrease_service_inventory_count(self, order: Order) -> None:
    #     # move to order class ?
    #     service = order.slot.schedule.service
    #     for consumable in service.consumables:
    #         consumable.inventory.stock_count = CountNumber(consumable.inventory.stock_count - consumable.count)
    #
    #
    # def _increase_service_inventory_count(self) -> None:
    #     service = self.slot.schedule.service
    #     for consumable in service.consumables:
    #         consumable.inventory.stock_count = CountNumber(consumable.inventory.stock_count + consumable.count)

    def __eq__(self, other):
        return (
            # self.user,
            self.user_id,
            self.slot,
            self.point_uses,
            self.total_amount,
            self.date_add.strftime("%Y-%m-%d %H:%M"),
        ) == (
            # other.user,
            other.user_id,
            other.slot,
            other.point_uses,
            other.total_amount,
            other.date_add.strftime("%Y-%m-%d %H:%M"),
        )

    def to_dict(self) -> dict:
        # user = self.user.to_dict() if self.user else None
        slot = self.slot.to_dict() if self.slot else None
        return {
            "id": self.id,
            "point_uses": self.point_uses.as_generic_type(),
            "promotion_sale": self.promotion_sale.as_generic_type(),
            "total_amount": self.total_amount.as_generic_type(),
            "date_add": self.date_add,
            "photo_before_path": self.photo_before_path,
            "photo_after_path": self.photo_after_path,
            # "user": user,
            "user_id": self.user_id,
            "slot": slot,
        }


# class OrderCheckCorrectSlotDomainService:
#     def check_slot_is_correct():
#         if slot in occupied_slots:
#             raise SlotOccupiedException()
#
#
#         # if not slot_for_schedule.check_slot_time_is_free(slot_time=time_start, occupied_slots=occupied_slots):
#         #     raise SlotOccupiedException()
#
#         if service not in slot.schedule.master.services
