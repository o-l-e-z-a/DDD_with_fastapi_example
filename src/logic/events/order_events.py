from dataclasses import dataclass

from src.domain.orders.events import OrderCreatedEvent
from src.infrastructure.db.uows.schedule_uow import SQLAlchemyScheduleUnitOfWork
from src.logic.events.base import EventHandler


@dataclass
class OrderCreatedEmailEventHandler(EventHandler[OrderCreatedEvent]):
    uow: SQLAlchemyScheduleUnitOfWork

    async def handle(self, event: OrderCreatedEvent) -> None:
        print(f"{self.__class__.__name__}, event: {event}")
        return None


@dataclass
class OrderCreatedPointIncreaseEventHandler(EventHandler[OrderCreatedEvent]):
    uow: SQLAlchemyScheduleUnitOfWork

    async def handle(self, event: OrderCreatedEvent):
        print(f"{self.__class__.__name__}, event: {event}")
        return None
