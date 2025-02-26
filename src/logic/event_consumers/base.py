from abc import ABC
from dataclasses import dataclass
from typing import ClassVar

import aio_pika

from src.logic.mediator.base import Mediator


@dataclass(frozen=True)
class BaseEventConsumer(ABC):
    mediator: Mediator
    exchange_name: ClassVar[str]
    queue_name: ClassVar[str]
    routing_key: ClassVar[str]

    async def __call__(
        self,
        message: aio_pika.abc.AbstractIncomingMessage,
    ) -> None: ...
