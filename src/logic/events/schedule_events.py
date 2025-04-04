from dataclasses import dataclass

from dataclasses_json import dataclass_json

from src.domain.base.events import BaseEvent
from src.domain.schedules.events import OrderCancelledEvent
from src.infrastructure.db.uows.schedule_uow import SQLAlchemyScheduleQueryUnitOfWork, SQLAlchemyScheduleUnitOfWork
from src.infrastructure.logger_adapter.logger import init_logger
from src.logic.events.base import BrokerEventhandler, EventHandler

logger = init_logger(__name__)


@dataclass_json
@dataclass
class OrderCreatedEvent(BaseEvent):
    order_id: int
    user_id: int
    schedule_id: int
    slot_time_start: str
    service_name: str
    service_price: int


@dataclass
class OrderCreatedEmailEventHandler(EventHandler[OrderCreatedEvent]):
    uow: SQLAlchemyScheduleQueryUnitOfWork

    async def handle(self, event: OrderCreatedEvent) -> None:
        logger.debug(f"{self.__class__.__name__}, event: {event}")
        return None


@dataclass
class OrderCreatedBrokerEventHandler(BrokerEventhandler[OrderCreatedEvent]):
    uow: SQLAlchemyScheduleUnitOfWork
    exchange_name = "order_create"
    routing_key = "order_create"


@dataclass
class OrderCanceledBrokerEventHandler(BrokerEventhandler[OrderCancelledEvent]):
    uow: SQLAlchemyScheduleUnitOfWork
    exchange_name = "order_cancel"
    routing_key = "order_cancel"
