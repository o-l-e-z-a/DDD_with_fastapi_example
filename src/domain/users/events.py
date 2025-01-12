from dataclasses import dataclass

from src.domain.base.events import BaseEvent


@dataclass
class UserCreatedEvent(BaseEvent):
    user_id: int
