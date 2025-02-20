from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Type

from src.domain.base.events import BaseEvent
from src.logic.commands.base import CR, CT, BaseCommand, CommandHandler
from src.logic.events.base import ER, ET, EventHandler
from src.logic.exceptions.mediator_exceptions import (
    CommandHandlersNotRegisteredException,
    QueryHandlersNotRegisteredException,
)
from src.logic.mediator.command import CommandMediator
from src.logic.mediator.event import EventMediator
from src.logic.mediator.query import QueryMediator
from src.logic.queries.base import QR, QT, BaseQuery, QueryHandler


@dataclass(eq=False)
class Mediator(EventMediator, CommandMediator, QueryMediator):
    events_map: dict[Type[BaseEvent], list[EventHandler]] = field(
        default_factory=lambda: defaultdict(list),
        kw_only=True,
    )
    commands_map: dict[Type[BaseCommand], list[CommandHandler]] = field(
        default_factory=lambda: defaultdict(list),
        kw_only=True,
    )
    queries_map: dict[Type[BaseQuery], QueryHandler] = field(
        default_factory=dict,
        kw_only=True,
    )

    def register_event(self, event: Type[ET], event_handlers: Iterable[EventHandler[ET, ER]]):
        self.events_map[event].extend(event_handlers)

    def register_command(self, command: Type[CT], command_handlers: Iterable[CommandHandler[CT, CR]]):
        self.commands_map[command].extend(command_handlers)

    def register_query(self, query: Type[QT], query_handler: QueryHandler[QT, QR]):
        self.queries_map[query] = query_handler

    async def publish(self, events: Iterable[BaseEvent]) -> Iterable[ER]:
        result = []

        for event in events:
            event_type = event.__class__
            handlers: Iterable[EventHandler] = self.events_map[event_type]
            result.extend([await handler.handle(event) for handler in handlers])

        return result

    async def handle_command(self, command: BaseCommand) -> list[CR]:
        command_type = command.__class__
        handlers = self.commands_map.get(command_type)

        if not handlers:
            raise CommandHandlersNotRegisteredException(command_type)

        return [await handler.handle(command) for handler in handlers]

    async def handle_query(self, query: BaseQuery) -> QR:
        query_type = query.__class__
        handler = self.queries_map.get(query_type)

        if not handler:
            raise QueryHandlersNotRegisteredException(query_type)
        return await handler.handle(query=query)
