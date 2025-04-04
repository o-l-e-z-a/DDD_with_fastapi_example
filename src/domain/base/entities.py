from abc import ABC
from copy import copy
from dataclasses import dataclass, field

from src.domain.base.events import BaseEvent


@dataclass
class BaseEntity(ABC):
    def to_dict(self) -> dict: ...


@dataclass
class BaseEntityWithIntIdAndEvents(BaseEntity):
    id: int = field(init=False, hash=False, repr=False, compare=False)
    _events: list[BaseEvent] = field(
        default_factory=list,
        kw_only=True,
    )

    def register_event(self, event: BaseEvent) -> None:
        self._events.append(event)

    def pull_events(self) -> list[BaseEvent]:
        registered_events = copy(self._events)
        self._events.clear()

        return registered_events
