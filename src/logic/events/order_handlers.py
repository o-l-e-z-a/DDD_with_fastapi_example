from dataclasses import dataclass


from src.domain.orders.events import OrderCreatedEvent
from src.logic.events.base import EventHandler
from src.logic.uows.schedule_uow import SQLAlchemyScheduleUnitOfWork


@dataclass
class OrderCreatedEmailEventHandler(EventHandler[OrderCreatedEvent, None]):
    uow: SQLAlchemyScheduleUnitOfWork

    async def handle(self, event: OrderCreatedEvent) -> None:
        print(f"{self.__class__.__name__}, event: {event}")


@dataclass
class OrderCreatedPointIncreaseEventHandler(EventHandler[OrderCreatedEvent, None]):
    uow: SQLAlchemyScheduleUnitOfWork

    async def handle(self, event: OrderCreatedEvent) -> None:
        print(f"{self.__class__.__name__}, event: {event}")
