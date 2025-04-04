from dataclasses import dataclass

from dataclasses_json import dataclass_json

from src.domain.base.events import BaseEvent
from src.infrastructure.db.uows.users_uow import SQLAlchemyUsersUnitOfWork
from src.logic.events.base import BrokerEventhandler


@dataclass_json
@dataclass
class UserCreatedEvent(BaseEvent):
    user_id: int
    email: str
    first_name: str
    last_name: str


@dataclass
class UserCreatedEventHandler(BrokerEventhandler[UserCreatedEvent]):
    uow: SQLAlchemyUsersUnitOfWork
    exchange_name = "user_create"
    routing_key = "user_create"
