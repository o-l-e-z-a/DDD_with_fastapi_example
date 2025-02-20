from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Type

from src.domain.base.events import BaseEvent
from src.logic.events.base import ER, ET, EventHandler


@dataclass(eq=False)
class EventMediator(ABC):
    events_map: dict[Type[BaseEvent], list[EventHandler]] = field(
        default_factory=lambda: defaultdict(list),
        kw_only=True,
    )

    @abstractmethod
    def register_event(self, event: Type[ET], event_handlers: Iterable[EventHandler[ET, ER]]): ...

    @abstractmethod
    async def publish(self, events: Iterable[BaseEvent]) -> Iterable[ER]: ...
