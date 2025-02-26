from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar, Generic, TypeVar

from src.domain.base.events import BaseEvent
from src.infrastructure.broker.rabbit.producer import Producer
from src.infrastructure.db.uows.base import AbstractUnitOfWork

ET = TypeVar("ET", bound=BaseEvent)
ER = TypeVar("ER", bound=Any)


@dataclass
class EventHandler(ABC, Generic[ET]):
    uow: AbstractUnitOfWork
    message_broker: Producer
    exchange_name: ClassVar[str]
    routing_key: ClassVar[str]

    @abstractmethod
    async def handle(self, event: ET) -> None: ...
