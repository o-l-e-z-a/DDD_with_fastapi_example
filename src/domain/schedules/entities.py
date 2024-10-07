from dataclasses import dataclass, field
from datetime import date

from src.domain.base.values import CountNumber, Name, PositiveIntNumber
from src.domain.schedules.values import END_HOUR, SLOT_DELTA, START_HOUR, SlotTime
from src.domain.users.entities import User


@dataclass
class Inventory:
    # id: int
    name: Name
    unit: Name
    stock_count: CountNumber


@dataclass
class Consumable:
    #     id: int
    inventory: Inventory
    count: PositiveIntNumber


@dataclass
class Service:
    #     id: int
    name: Name
    description: str
    price: PositiveIntNumber
    consumables: list[Consumable] = field(default_factory=list)


@dataclass
class Master:
    #     id: int
    description: str
    user: User
    services: list[Service] = field(default_factory=list)


@dataclass
class Schedule:
    #     id: int
    day: date
    master: Master
    service: Service


@dataclass
class Slot:
    #     id: int
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
