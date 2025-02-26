from dataclasses import dataclass

from src.domain.base.events import BaseEvent
from src.infrastructure.broker.converters import convert_event_to_broker_message
from src.logic.events.base import EventHandler


@dataclass
class UserCreatedEvent(BaseEvent):
    user_id: int
    email: str
    first_name: str
    last_name: str


from src.infrastructure.db.uows.schedule_uow import SQLAlchemyScheduleUnitOfWork


@dataclass
class UserCreatedEventHandler(EventHandler[UserCreatedEvent]):
    uow: SQLAlchemyScheduleUnitOfWork
    exchange_name = "user_create"
    routing_key = "user_create"

    async def handle(self, event: UserCreatedEvent):
        await self.message_broker.declare_exchange(self.exchange_name)
        await self.message_broker.publish_message(
            message_data=convert_event_to_broker_message(event),
            exchange_name=self.exchange_name,
            routing_key=self.routing_key,
        )
