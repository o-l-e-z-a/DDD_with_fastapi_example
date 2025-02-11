import asyncio

from collections import defaultdict
from datetime import date, timedelta
from typing import Type

from dishka import AnyOf, Provider, Scope, make_async_container, provide

from src.domain.orders.events import OrderCreatedEvent
from src.infrastructure.db.provider import DBProvider
from src.logic.commands.base import CT, CommandHandler
from src.logic.commands.schedule_commands import (
    AddMasterCommand,
    AddMasterCommandHandler,
    AddOrderCommand,
    AddOrderCommandHandler,
    AddScheduleCommand,
    AddScheduleCommandHandler,
    CancelOrderCommand,
    CancelOrderCommandHandler,
    UpdateOrderCommand,
    UpdateOrderCommandHandler,
)
from src.logic.commands.user_commands import AddUserCommand, AddUserCommandHandler
from src.logic.events.base import ET, EventHandler
from src.logic.events.order_handlers import OrderCreatedEmailEventHandler, OrderCreatedPointIncreaseEventHandler
from src.logic.mediator.base import Mediator
from src.logic.mediator.command import CommandMediator
from src.logic.mediator.event import EventMediator
from src.logic.uows.order_uow import SQLAlchemyOrderUnitOfWork
from src.logic.uows.schedule_uow import SQLAlchemyScheduleUnitOfWork
from src.logic.uows.users_uow import SQLAlchemyUsersUnitOfWork
from src.presentation.api.settings import Settings, settings


class MyProvider(Provider):
    scope = Scope.APP

    user_uow = provide(SQLAlchemyUsersUnitOfWork)
    schedule_uow = provide(SQLAlchemyScheduleUnitOfWork)
    order_uow = provide(SQLAlchemyOrderUnitOfWork)

    @provide()
    def get_cmd_with_cmd_handlers_dict(self) -> dict[Type[CT], list[CommandHandler]]:
        return defaultdict(list)

    @provide()
    def get_cmd_with_event_handlers_dict(self) -> dict[Type[ET], list[EventHandler]]:
        return defaultdict(list)

    @provide(scope=Scope.APP, provides=AnyOf[EventMediator, CommandMediator])
    def init_mediator(
        self,
        user_uow: SQLAlchemyUsersUnitOfWork,
        schedule_uow: SQLAlchemyScheduleUnitOfWork,
        order_uow: SQLAlchemyOrderUnitOfWork,
    ) -> Mediator:
        mediator = Mediator()
        mediator.register_command(AddUserCommand, [AddUserCommandHandler(mediator=mediator, uow=user_uow)])
        mediator.register_command(AddOrderCommand, [AddOrderCommandHandler(mediator=mediator, uow=schedule_uow)])
        mediator.register_command(UpdateOrderCommand, [UpdateOrderCommandHandler(mediator=mediator, uow=schedule_uow)])
        mediator.register_command(CancelOrderCommand, [CancelOrderCommandHandler(mediator=mediator, uow=schedule_uow)])
        mediator.register_command(AddMasterCommand, [AddMasterCommandHandler(mediator=mediator, uow=schedule_uow)])
        mediator.register_command(AddScheduleCommand, [AddScheduleCommandHandler(mediator=mediator, uow=schedule_uow)])
        mediator.register_event(
            OrderCreatedEvent,
            [OrderCreatedPointIncreaseEventHandler(uow=schedule_uow), OrderCreatedEmailEventHandler(uow=schedule_uow)],
        )
        return mediator


# def get_mediator_with_schedule_register_handlers():
#     mediator = Mediator()
#     uow = SQLAlchemyScheduleUnitOfWork()
#     mediator.register_command(AddOrderCommand, [AddOrderCommandHandler(mediator=mediator, uow=uow)])
#     mediator.register_command(UpdateOrderCommand, [UpdateOrderCommandHandler(mediator=mediator, uow=uow)])
#     mediator.register_command(CancelOrderCommand, [CancelOrderCommandHandler(mediator=mediator, uow=uow)])
#     mediator.register_command(AddMasterCommand, [AddMasterCommandHandler(mediator=mediator, uow=uow)])
#     mediator.register_command(AddScheduleCommand, [AddScheduleCommandHandler(mediator=mediator, uow=uow)])
#     mediator.register_event(
#         OrderCreatedEvent,
#         [OrderCreatedEmailEventHandler(uow=uow), OrderCreatedPointIncreaseEventHandler(uow=uow)],
#     )
#     return mediator


def get_mediator_with_user_register_handlers():
    mediator = Mediator()
    uow = SQLAlchemyUsersUnitOfWork()
    mediator.register_command(AddUserCommand, [AddUserCommandHandler(mediator=mediator, uow=uow)])
    return mediator


async def create_user():
    mediator = await container.get(Mediator)
    await mediator.handle_command(
        AddUserCommand(
            email="safas@wsefg.com",
            first_name="sad",
            last_name="asdas",
            telephone="880055534323",
            password="asdas@13H",
        )
    )


async def add_master():
    mediator = await container.get(Mediator)
    data = AddMasterCommand(
        description="asdasdasdasd",
        user_id=11,
        services_id=[1, 2],
    )
    await mediator.handle_command(data)


async def add_schedule():
    mediator = await container.get(Mediator)
    data = AddScheduleCommand(day=date.today() + timedelta(days=1), master_id=2)
    print(await mediator.handle_command(data))


async def add_order():
    mediator = await container.get(Mediator)
    order_data = AddOrderCommand(
        slot_id=35,
        service_id=1,
        user_id=13,
    )
    await mediator.handle_command(order_data)


async def update_order():
    mediator = await container.get(Mediator)
    order_data = UpdateOrderCommand(
        slot_id=37,
        order_id=22,
        user_id=13,
    )
    await mediator.handle_command(order_data)


async def delete_order():
    mediator = await container.get(Mediator)
    user_id = 13
    order_data = CancelOrderCommand(user_id=user_id, order_id=19)
    await mediator.handle_command(order_data)


if __name__ == "__main__":
    container = make_async_container(MyProvider(), DBProvider(), context={Settings: settings})
    asyncio.new_event_loop().run_until_complete(add_order())
