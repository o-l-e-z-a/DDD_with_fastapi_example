from dataclasses import dataclass

from src.domain.base.events import BaseEvent
from src.domain.schedules.events import OrderCancelledEvent
from src.infrastructure.db.uows.order_uow import SQLAlchemyOrderUnitOfWork
from src.logic.events.base import BrokerEventhandler


@dataclass(kw_only=True)
class OrderPayedEvent(BaseEvent):
    order_payment_id: int
    user_point_id: int
    point_uses: int


@dataclass
class OrderPayedEventHandler(BrokerEventhandler[OrderCancelledEvent]):
    uow: SQLAlchemyOrderUnitOfWork
    exchange_name = "order_payed"
    routing_key = "order_payed"
