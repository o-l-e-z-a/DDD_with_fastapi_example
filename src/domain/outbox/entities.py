from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from src.domain.base.entities import BaseEntity
from src.domain.outbox.values import MessageType


@dataclass
class OutboxMessage(BaseEntity):
    type: MessageType
    data: dict[str, Any]
    id: UUID = field(default_factory=uuid4, kw_only=True)
    occurred_at: datetime = field(default_factory=datetime.now, kw_only=True)
    processed_at: datetime | None = None

    def update_process_at(self):
        self.processed_at = datetime.now()
