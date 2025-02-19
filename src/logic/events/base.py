from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from src.domain.base.events import BaseEvent
from src.infrastructure.db.uows.base import AbstractUnitOfWork

ET = TypeVar("ET", bound=BaseEvent)
ER = TypeVar("ER", bound=Any)


@dataclass
class EventHandler(ABC, Generic[ET, ER]):
    uow: AbstractUnitOfWork

    @abstractmethod
    def handle(self, event: ET) -> ER: ...
