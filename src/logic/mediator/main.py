import asyncio

from datetime import date, timedelta

from dishka import Provider, Scope, from_context, make_async_container, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from src.domain.orders.events import OrderCreatedEvent
from src.infrastructure.db.config import get_async_engine, get_async_session_factory
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
from src.logic.events.order_handlers import OrderCreatedEmailEventHandler, OrderCreatedPointIncreaseEventHandler
from src.logic.mediator.base import Mediator
from src.logic.uows.schedule_uow import SQLAlchemyScheduleUnitOfWork
from src.logic.uows.users_uow import SQLAlchemyUsersUnitOfWork
from src.presentation.api.settings import Settings, settings


class MyProvider(Provider):
    scope = Scope.APP
    settings = from_context(Settings)

    user_uow = provide(SQLAlchemyUsersUnitOfWork)
    schedule_uow = provide(SQLAlchemyUsersUnitOfWork)
    order_uow = provide(SQLAlchemyUsersUnitOfWork)

    add_user_cmd_handler = provide(AddUserCommandHandler)
    add_order_cmd_handler = provide(AddUserCommandHandler)
    update_order_cmd_handler = provide(AddUserCommandHandler)
    cancel_order_cmd_handler = provide(AddUserCommandHandler)
    add_master_cmd_handler = provide(AddUserCommandHandler)
    add_schedule_cmd_handler = provide(AddUserCommandHandler)

    @provide(scope=Scope.APP)
    def engine(self, setting: Settings) -> AsyncEngine:
        engine = get_async_engine(setting)
        return engine

    @provide(scope=Scope.APP)
    def get_async_session_maker(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return get_async_session_factory(engine)

    @provide()
    def get_mediator(
        self,
        add_user_cmd_handler: AddUserCommandHandler,
        add_order_cmd_handler: AddUserCommandHandler,
        update_order_cmd_handler: AddUserCommandHandler,
        cancel_order_cmd_handler: AddUserCommandHandler,
        add_master_cmd_handler: AddUserCommandHandler,
        add_schedule_cmd_handler: AddUserCommandHandler,
    ) -> Mediator:
        mediator = Mediator()
        mediator.register_command(AddUserCommand, [add_user_cmd_handler])
        mediator.register_command(AddOrderCommand, [add_order_cmd_handler])
        mediator.register_command(UpdateOrderCommand, [update_order_cmd_handler])
        mediator.register_command(CancelOrderCommand, [cancel_order_cmd_handler])
        mediator.register_command(AddMasterCommand, [add_master_cmd_handler])
        mediator.register_command(AddScheduleCommand, [add_schedule_cmd_handler])
        return mediator


def get_mediator_with_user_register_handlers():
    mediator = Mediator()
    uow = SQLAlchemyUsersUnitOfWork()
    mediator.register_command(AddUserCommand, [AddUserCommandHandler(mediator=mediator, uow=uow)])
    return mediator


async def create_user():
    mediator = get_mediator_with_user_register_handlers()
    await mediator.handle_command(
        AddUserCommand(
            email="safas@wsefg.com",
            first_name="sad",
            last_name="asdas",
            telephone="880055534323",
            password="asdas@13H",
        )
    )


def get_mediator_with_schedule_register_handlers():
    mediator = Mediator()
    uow = SQLAlchemyScheduleUnitOfWork()
    mediator.register_command(AddOrderCommand, [AddOrderCommandHandler(mediator=mediator, uow=uow)])
    mediator.register_command(UpdateOrderCommand, [UpdateOrderCommandHandler(mediator=mediator, uow=uow)])
    mediator.register_command(CancelOrderCommand, [CancelOrderCommandHandler(mediator=mediator, uow=uow)])
    mediator.register_command(AddMasterCommand, [AddMasterCommandHandler(mediator=mediator, uow=uow)])
    mediator.register_command(AddScheduleCommand, [AddScheduleCommandHandler(mediator=mediator, uow=uow)])
    mediator.register_event(
        OrderCreatedEvent,
        [OrderCreatedEmailEventHandler(uow=uow), OrderCreatedPointIncreaseEventHandler(uow=uow)],
    )
    return mediator


async def add_master():
    mediator = get_mediator_with_schedule_register_handlers()
    data = AddMasterCommand(
        description="asdasdasdasd",
        user_id=11,
        services_id=[1, 2],
    )
    await mediator.handle_command(data)


async def add_schedule():
    mediator = get_mediator_with_schedule_register_handlers()
    data = AddScheduleCommand(day=date.today() + timedelta(days=1), master_id=2)
    print(await mediator.handle_command(data))


async def add_order():
    # mediator = get_mediator_with_schedule_register_handlers()
    mediator = await container.get(Mediator)
    order_data = AddOrderCommand(
        slot_id=36,
        service_id=1,
        user_id=13,
    )
    await mediator.handle_command(order_data)


async def update_order():
    mediator = get_mediator_with_schedule_register_handlers()
    order_data = UpdateOrderCommand(
        slot_id=37,
        order_id=22,
        user_id=13,
    )
    await mediator.handle_command(order_data)


async def delete_order():
    mediator = get_mediator_with_schedule_register_handlers()
    user_id = 13
    order_data = CancelOrderCommand(user_id=user_id, order_id=19)
    await mediator.handle_command(order_data)


if __name__ == "__main__":
    container = make_async_container(MyProvider(settings))
    asyncio.new_event_loop().run_until_complete(add_order())
