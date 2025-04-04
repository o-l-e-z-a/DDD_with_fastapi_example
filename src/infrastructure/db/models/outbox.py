from __future__ import annotations

from datetime import datetime
from typing import Any, Self

from sqlalchemy import CHAR, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.outbox import entities
from src.domain.outbox.values import MessageType
from src.infrastructure.db.models.base import Base


class OutboxMessage(Base):
    __tablename__ = "outbox_messages"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True)
    occurred_at: Mapped[datetime]
    type: Mapped[str]
    data: Mapped[dict[str, Any]] = mapped_column(JSON)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    @classmethod
    def from_entity(cls, entity: entities.OutboxMessage) -> Self:
        return cls(
            id=str(entity.id),
            type=entity.type.as_generic_type(),
            data=entity.data,
            occurred_at=entity.occurred_at,
            processed_at=entity.processed_at,
        )

    def to_domain(self) -> entities.OutboxMessage:
        return entities.OutboxMessage(
            id=self.id,
            occurred_at=self.occurred_at,
            processed_at=self.processed_at,
            type=MessageType(self.type),
            data=self.data,
        )

    def __str__(self) -> str:
        return (
            f"OutboxMessage(id={self.id}, occurred_at={self.occurred_at}, "
            f"type={self.type}, processed_at={self.processed_at})"
        )
