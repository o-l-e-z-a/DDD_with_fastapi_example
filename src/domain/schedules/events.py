from dataclasses import dataclass

from src.domain.base.events import BaseEvent


@dataclass
class ScheduleCreatedEvent(BaseEvent):
    schedule_id: int


@dataclass()
class OrderCancelledEvent(BaseEvent):
    order_id: int
    user_id: int
    service_id: int
