from dataclasses import dataclass, field
from datetime import date

from src.domain.base.entities import BaseEntity
from src.domain.base.values import CountNumber, Name, PositiveIntNumber
from src.domain.schedules.values import END_HOUR, SLOT_DELTA, START_HOUR, SlotTime
from src.domain.users.entities import User


@dataclass
class Inventory(BaseEntity):
    id: int = field(init=False)
    name: Name
    unit: Name
    stock_count: CountNumber


@dataclass
class Consumable(BaseEntity):
    id: int = field(init=False)
    inventory: Inventory
    count: PositiveIntNumber


@dataclass
class Service(BaseEntity):
    id: int = field(init=False)
    name: Name
    description: str
    price: PositiveIntNumber
    consumables: set[Consumable] = field(default_factory=set)


@dataclass
class Master(BaseEntity):
    id: int = field(init=False)
    description: str
    user: User
    services: set[Service] = field(default_factory=set)


@dataclass
class Schedule(BaseEntity):
    id: int = field(init=False)
    day: date
    master: Master
    service: Service


@dataclass
class Slot(BaseEntity):
    id: int = field(init=False)
    time_start: SlotTime
    schedule: Schedule

    def __eq__(self, other) -> bool:
        return (self.time_start, self.schedule.id) == (other.time_start, other.schedule.id)

    def __gt__(self, other) -> bool:
        if self.schedule.day > other.schedule.day:
            return True
        elif self.schedule.day < other.schedule.day:
            return False
        else:
            if self.time_start > other.time_start:
                return True
            return False


class SlotsForSchedule:
    def get_free_slots(self, occupied_slots: list[Slot]) -> list[SlotTime]:
        all_day_slots = {SlotTime(f"{hour}:00") for hour in range(START_HOUR, END_HOUR + SLOT_DELTA)}
        occupied_slots_time = {occupied_slot.time_start for occupied_slot in occupied_slots}
        return sorted(all_day_slots.difference(occupied_slots_time))

    def check_slot_time_is_free(self, slot_time: SlotTime, occupied_slots: list[Slot]) -> bool:
        free_slots = self.get_free_slots(occupied_slots)
        return True if slot_time in free_slots else False
