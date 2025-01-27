from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Type

from src.domain.base.events import BaseEvent
from src.logic.commands.base import CR, CT, BaseCommand, CommandHandler
from src.logic.events.base import ER, ET, EventHandler
from src.logic.exceptions.message_bus import CommandHandlersNotRegisteredException
from src.logic.mediator.command import CommandMediator
from src.logic.mediator.event import EventMediator


@dataclass(eq=False)
class Mediator(EventMediator, CommandMediator):
    events_map: dict[Type[ET], list[EventHandler]] = field(
        default_factory=lambda: defaultdict(list),
        kw_only=True,
    )
    commands_map: dict[Type[CT], list[CommandHandler]] = field(
        default_factory=lambda: defaultdict(list),
        kw_only=True,
    )

    def register_event(self, event: Type[ET], event_handlers: Iterable[EventHandler[ET, ER]]):
        self.events_map[event].extend(event_handlers)

    def register_command(self, command: Type[CT], command_handlers: Iterable[CommandHandler[CT, CR]]):
        self.commands_map[command].extend(command_handlers)

    async def publish(self, events: Iterable[BaseEvent]) -> Iterable[ER]:
        result = []

        for event in events:
            handlers: Iterable[EventHandler] = self.events_map[event.__class__]
            result.extend([await handler.handle(event) for handler in handlers])

        return result

    async def handle_command(self, command: BaseCommand) -> Iterable[CR]:
        command_type = command.__class__
        handlers = self.commands_map.get(command_type)

        if not handlers:
            raise CommandHandlersNotRegisteredException(command_type)

        return [await handler.handle(command) for handler in handlers]
