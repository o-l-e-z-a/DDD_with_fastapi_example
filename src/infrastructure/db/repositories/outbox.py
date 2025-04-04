import asyncpg

from sqlalchemy import null, select
from sqlalchemy.exc import IntegrityError

from src.domain.base.events import BaseEvent
from src.domain.outbox import entities
from src.domain.outbox.values import MessageType
from src.infrastructure.db.exceptions import InsertException, UpdateException
from src.infrastructure.db.models.outbox import OutboxMessage
from src.infrastructure.db.repositories.base import GenericSQLAlchemyRepository
from src.infrastructure.logger_adapter.logger import init_logger

logger = init_logger(__name__)


class OutboxMessageRepository(GenericSQLAlchemyRepository[OutboxMessage, entities.OutboxMessage]):
    model = OutboxMessage

    async def bulk_add(self, events: list[BaseEvent]) -> list[entities.OutboxMessage]:
        results = []
        for event in events:
            result = await self.add_from_event(event)
            results.append(result)
        return results

    async def add_from_event(self, event: BaseEvent) -> entities.OutboxMessage:
        data = event.to_json()
        logger.debug(f"data: {data}")
        entity = entities.OutboxMessage(
            type=MessageType(f"{type(event).__module__}.{type(event).__name__}"),
            data=data,
        )
        model = self.model.from_entity(entity)
        logger.debug(f"model: {model}")
        self.session.add(model)
        try:
            await self.session.flush()
        except IntegrityError as err:
            raise InsertException(entity=entity, detail=str(err.args))
        return model.to_domain()

    async def get_messages_to_publish(self) -> list[entities.OutboxMessage]:
        query = (
            select(OutboxMessage)
            .where(OutboxMessage.processed_at == null())
            .order_by(OutboxMessage.occurred_at)
            .with_for_update(nowait=True)
            .limit(10)
        )
        try:
            result = await self.session.execute(query)
        except asyncpg.exceptions.LockNotAvailableError:
            return []
        return [el.to_domain() for el in result.scalars().all()]

    async def mark_as_published(self, entity: entities.OutboxMessage) -> None:
        model = self.model.from_entity(entity)
        await self.session.merge(model)
        try:
            await self.session.flush()
        except IntegrityError as err:
            raise UpdateException(entity=entity, detail=str(err.args))
