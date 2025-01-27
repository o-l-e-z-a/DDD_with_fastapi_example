from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from src.infrastructure.db.uow import AbstractUnitOfWork
from src.logic.mediator.event import EventMediator


class BaseCommand(BaseModel):
    class Config:
        from_attributes = True


CT = TypeVar("CT", bound=BaseCommand)
CR = TypeVar("CR", bound=Any)


@dataclass(frozen=True)
class CommandHandler(ABC, Generic[CT, CR]):
    uow: AbstractUnitOfWork
    mediator: EventMediator

    @abstractmethod
    async def handle(self, command: CT) -> CR: ...
