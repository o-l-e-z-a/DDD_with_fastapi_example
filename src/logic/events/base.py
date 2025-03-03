from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar, Generic, TypeVar

from src.domain.base.events import BaseEvent
from src.infrastructure.broker.converters import convert_event_to_broker_message
from src.infrastructure.broker.rabbit.producer import Producer
from src.infrastructure.db.uows.base import AbstractUnitOfWork

ET = TypeVar("ET", bound=BaseEvent)
ER = TypeVar("ER", bound=Any)


@dataclass
class EventHandler(ABC, Generic[ET]):
    uow: AbstractUnitOfWork

    @abstractmethod
    async def handle(self, event: ET) -> None: ...


@dataclass
class BrokerEventhandler(EventHandler, Generic[ET]):
    message_broker: Producer
    exchange_name: ClassVar[str]
    routing_key: ClassVar[str]

    async def handle(self, event: ET) -> None:
        converted_event = convert_event_to_broker_message(event)
        await self.message_broker.declare_exchange(self.exchange_name)
        await self.message_broker.publish_message(
            message_data=converted_event,
            exchange_name=self.exchange_name,
            routing_key=self.routing_key,
        )
