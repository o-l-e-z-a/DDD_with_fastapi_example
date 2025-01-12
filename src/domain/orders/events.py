from dataclasses import dataclass

from src.domain.base.events import BaseEvent


@dataclass
class OrderCreatedEvent(BaseEvent):
    order_id: int
    user_id: int
    slot_id: int
    point_uses: int
    total_amount: int
