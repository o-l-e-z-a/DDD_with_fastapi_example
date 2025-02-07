from __future__ import annotations

import enum

from dataclasses import dataclass, field
from datetime import date, datetime

from src.domain.base.entities import BaseEntity
from src.domain.base.values import Name, PositiveIntNumber
from src.domain.orders.events import OrderCreatedEvent, OrderDeletedEvent
from src.domain.schedules.exceptions import SlotOccupiedException, SlotServiceInvalidException
from src.domain.schedules.values import END_HOUR, SLOT_DELTA, START_HOUR, SlotTime


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
    user_id: int
    services_id: list[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "description": self.description,
            "user_id": self.user_id,
            "services_id": [service_id for service_id in self.services_id],
        }


@dataclass()
class Schedule(BaseEntity):
    day: date
    master_id: int
    slots: list[Slot]

    @classmethod
    def add(cls, day: date, master_id: int):
        all_day_slots = [
            Slot(
                time_start=SlotTime(f"{hour}:00"),
            )
            for hour in range(START_HOUR, END_HOUR + SLOT_DELTA)
        ]

        schedule = cls(day=day, master_id=master_id, slots=all_day_slots)
        return schedule

    def get_free_slots(self, occupied_slots: list[Slot]) -> list[Slot]:
        occupied_slots_time = {occupied_slot for occupied_slot in occupied_slots}
        difference = set(self.slots).difference(occupied_slots_time)
        return sorted(difference)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "day": self.day,
            "master_id": self.master_id,
            "slots": self.slots
        }


@dataclass()
class Slot(BaseEntity):
    schedule_id: int = field(init=False, hash=False, repr=True, compare=False)
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
        return {"id": self.id, "time_start": self.time_start.as_generic_type(), "schedule_id": self.schedule_id}


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
    def add(
        cls,
        user_id: int,
        service_id: int,
        slot_id: int,
        schedule_master_services: list[Service],
        occupied_slots: list[Slot]
    ) -> Order:
        if slot_id in [slot.id for slot in occupied_slots]:
            raise SlotOccupiedException()

        if service_id not in [service.id for service in schedule_master_services]:
            raise SlotServiceInvalidException()

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

    def update_slot_time(self, slot_id: int, occupied_slots: list[Slot]):
        if slot_id in occupied_slots:
            raise SlotOccupiedException()
        self.slot_id = slot_id

    def cancel(self):
        self.status = OrderStatus.CANCELLED
        self.register_event(
            OrderDeletedEvent(
                user_id=self.user_id,
                service_id=self.service_id,
                slot_id=self.slot_id,
            )
        )

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
            self.user_id,
            self.slot_id,
            self.service_id,
            self.date_add.strftime("%Y-%m-%d %H:%M"),
        ) == (
            other.user_id,
            other.slot_id,
            other.service_id,
            other.date_add.strftime("%Y-%m-%d %H:%M"),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "date_add": self.date_add,
            "photo_before_path": self.photo_before_path,
            "photo_after_path": self.photo_after_path,
            "user_id": self.user_id,
            "slot_id": self.slot_id,
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
