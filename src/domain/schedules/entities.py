from dataclasses import dataclass, field
from datetime import date

from src.domain.base.entities import BaseEntity
from src.domain.base.values import CountNumber, Name, PositiveIntNumber
from src.domain.schedules.values import END_HOUR, SLOT_DELTA, START_HOUR, SlotTime
from src.domain.users.entities import User


@dataclass()
class Inventory(BaseEntity):
    name: Name
    unit: Name
    stock_count: CountNumber

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name.as_generic_type(),
            'unit': self.unit.as_generic_type(),
            'stock_count': self.stock_count.as_generic_type(),
        }


@dataclass()
class Consumable(BaseEntity):
    inventory: Inventory
    count: PositiveIntNumber

    def to_dict(self) -> dict:
        inventory = self.inventory.to_dict() if self.inventory else None
        return {
            'id': self.id,
            'count': self.count.as_generic_type(),
            'inventory': inventory
        }


@dataclass()
class Service(BaseEntity):
    name: Name
    description: str
    price: PositiveIntNumber
    consumables: list[Consumable] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name.as_generic_type(),
            'price': self.price.as_generic_type(),
            'description': self.description,
            'consumables': [consumable.to_dict() for consumable in self.consumables]
        }


@dataclass()
class Master(BaseEntity):
    description: str
    user: User
    services: list[Service] = field(default_factory=list)

    def to_dict(self) -> dict:
        user = self.user.to_dict() if self.user else None
        return {
            'id': self.id,
            'description': self.description,
            'user': user,
            'services': [service.to_dict() for service in self.services]
        }


@dataclass()
class Schedule(BaseEntity):
    day: date
    master: Master
    service: Service

    def to_dict(self) -> dict:
        master = self.master.to_dict() if self.master else None
        service = self.service.to_dict() if self.service else None
        return {
            'id': self.id,
            'day': self.day,
            'master': master,
            'service': service
        }


@dataclass()
class Slot(BaseEntity):
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

    def to_dict(self) -> dict:
        schedule = self.schedule.to_dict() if self.schedule else None
        return {
            'id': self.id,
            'time_start': self.time_start.as_generic_type(),
            'schedule': schedule
        }


class SlotsForSchedule:
    def get_free_slots(self, occupied_slots: list[Slot]) -> list[SlotTime]:
        all_day_slots = {SlotTime(f"{hour}:00") for hour in range(START_HOUR, END_HOUR + SLOT_DELTA)}
        occupied_slots_time = {occupied_slot.time_start for occupied_slot in occupied_slots}
        return sorted(all_day_slots.difference(occupied_slots_time))

    def check_slot_time_is_free(self, slot_time: SlotTime, occupied_slots: list[Slot]) -> bool:
        free_slots = self.get_free_slots(occupied_slots)
        return True if slot_time in free_slots else False
