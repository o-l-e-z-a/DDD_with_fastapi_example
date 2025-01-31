from dataclasses import dataclass
from datetime import date

from src.domain.base.events import BaseEvent


@dataclass
class OrderCreatedEvent(BaseEvent):
    user_email: str
    user_first_name: str
    user_last_name: str
    slot_time: str
    schedule_day: date
    service_name: str
    point_uses: int
    total_amount: int


@dataclass()
class OrderDeletedEvent(BaseEvent):
    order_id: str
    user_email: str
    user_first_name: str
    user_last_name: str
    slot_time: str
    schedule_day: date
    service_name: str
    point_uses: int
    total_amount: int
