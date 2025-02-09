import asyncio

from datetime import date, timedelta

from src.domain.orders.events import OrderCreatedEvent
from src.domain.users.entities import User
from src.domain.users.values import Email, HumanName, Telephone
from src.logic.commands.order_commands import (
    TotalAmountDTO,
)
from src.logic.commands.schedule_commands import AddOrderCommand, AddOrderCommandCommandHandler, UpdateOrderCommand, \
    UpdateOrderCommandCommandHandler, DeleteOrderCommand, AddMasterCommand, AddMasterCommandCommandHandler, \
    CancelOrderCommandCommandHandler, AddScheduleCommand, AddScheduleCommandCommandHandler
from src.logic.commands.user_commands import AddUserCommand, AddUserCommandHandler
from src.logic.events.order_handlers import OrderCreatedEmailEventHandler, OrderCreatedPointIncreaseEventHandler
from src.logic.mediator.base import Mediator
from src.logic.uows.order_uow import SQLAlchemyOrderUnitOfWork
from src.logic.uows.schedule_uow import SQLAlchemyScheduleUnitOfWork
from src.logic.uows.users_uow import SQLAlchemyUsersUnitOfWork


def get_message_bus_with_user_register_handlers():
    mediator = Mediator()
    uow = SQLAlchemyUsersUnitOfWork()
    mediator.register_command(AddUserCommand, [AddUserCommandHandler(mediator=mediator, uow=uow)])
    return mediator


async def create_user():
    message_bus = get_message_bus_with_user_register_handlers()
    await message_bus.handle_command(
        AddUserCommand(
            email="safas@wsefg.com",
            first_name="sad",
            last_name="asdas",
            telephone="880055534323",
            password="asdas@13H",
        )
    )


def get_message_bus_with_schedule_register_handlers():
    mediator = Mediator()
    uow = SQLAlchemyScheduleUnitOfWork()
    mediator.register_command(AddOrderCommand, [AddOrderCommandCommandHandler(mediator=mediator, uow=uow)])
    mediator.register_command(UpdateOrderCommand, [UpdateOrderCommandCommandHandler(mediator=mediator, uow=uow)])
    mediator.register_command(DeleteOrderCommand, [CancelOrderCommandCommandHandler(mediator=mediator, uow=uow)])
    mediator.register_command(AddMasterCommand, [AddMasterCommandCommandHandler(mediator=mediator, uow=uow)])
    mediator.register_command(AddScheduleCommand, [AddScheduleCommandCommandHandler(mediator=mediator, uow=uow)])
    mediator.register_event(
        OrderCreatedEvent,
        [OrderCreatedEmailEventHandler(uow=uow), OrderCreatedPointIncreaseEventHandler(uow=uow)],
    )
    return mediator


async def add_master():
    message_bus = get_message_bus_with_schedule_register_handlers()
    data = AddMasterCommand(
        description="asdasdasdasd",
        user_id=11,
        services_id=[1, 2],
    )
    await message_bus.handle_command(data)


async def add_schedule():
    message_bus = get_message_bus_with_schedule_register_handlers()
    data = AddScheduleCommand(
        day=date.today() + timedelta(days=1),
        master_id=2
    )
    print(await message_bus.handle_command(data))


async def add_order():
    message_bus = get_message_bus_with_schedule_register_handlers()
    order_data = AddOrderCommand(
        slot_id=4,
        service_id=1,
        user_id=8,
    )
    await message_bus.handle_command(order_data)


async def update_order():
    message_bus = get_message_bus_with_schedule_register_handlers()
    order_data = UpdateOrderCommand(
        slot_id=5,
        order_id=2,
        user_id=8,
    )
    await message_bus.handle_command(order_data)


async def delete_order():
    message_bus = get_message_bus_with_schedule_register_handlers()
    user = User(
        email=Email("hue@grant.com"),
        first_name=HumanName("Hue"),
        last_name=HumanName("Grant"),
        telephone=Telephone("88005553434"),
        date_birthday=date(2024, 12, 6),
    )
    user.id = 13
    order_data = DeleteOrderCommand(user=user, order_id=19)
    await message_bus.handle_command(order_data)


if __name__ == "__main__":
    asyncio.new_event_loop().run_until_complete(update_order())
