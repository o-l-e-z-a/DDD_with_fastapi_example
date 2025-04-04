from dataclasses import dataclass

from dataclasses_json import dataclass_json

from src.domain.base.events import BaseEvent


@dataclass_json
@dataclass
class ScheduleCreatedEvent(BaseEvent):
    schedule_id: int


@dataclass_json
@dataclass()
class OrderCancelledEvent(BaseEvent):
    order_id: int
    user_id: int
