import asyncio
import importlib

from typing import Type

from src.domain.outbox.entities import OutboxMessage
from src.infrastructure.logger_adapter.logger import init_logger
from src.presentation.api.dependencies import setup_container

logger = init_logger(__name__)

from src.domain.outbox.values import MessageType
from src.infrastructure.db.uows.outbox_uow import SQLAlchemyOutboxUnitOfWork
from src.logic.mediator.base import Mediator


class OutboxProcessor:
    def __init__(self, uow: SQLAlchemyOutboxUnitOfWork, mediator: Mediator) -> None:
        self.uow = uow
        self.mediator = mediator

    def _get_cls_for(self, message_type: MessageType) -> Type:
        cls = None
        try:
            module = importlib.import_module(message_type.module_name)
            cls = getattr(module, message_type.class_name)
        except (AttributeError, ModuleNotFoundError) as err:
            logger.error(err)
        return cls

    async def process_outbox_message(self) -> None:
        async with self.uow:
            messages: list[OutboxMessage] = await self.uow.outbox.get_messages_to_publish()
            for message in messages:
                await self._publish_message(message)
            await self.uow.commit()

    async def _publish_message(self, message):
        event_cls = self._get_cls_for(message.type)
        if not event_cls:
            logger.error(f"not event_cls for message: {message}")
            return
        event = event_cls.from_json(message.data)
        logger.info(f"Start publishing event: {event} ...")
        publish_task = asyncio.create_task(self.mediator.publish([event]))
        # publish_task = asyncio.create_task(asyncio.sleep(5))
        try:
            await asyncio.wait_for(publish_task, timeout=30)
        except TimeoutError:
            return
        message.update_process_at()
        logger.debug(f"After update_process_at: {message} ...")
        await self.uow.outbox.mark_as_published(message)


async def start_outbox_process():
    container = setup_container()
    mediator = await container.get(Mediator)
    uow = await container.get(SQLAlchemyOutboxUnitOfWork)
    processor = OutboxProcessor(uow=uow, mediator=mediator)
    await processor.process_outbox_message()


if __name__ == "__main__":
    asyncio.run(start_outbox_process())
