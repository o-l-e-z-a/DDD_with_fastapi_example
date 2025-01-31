import asyncio

from datetime import date

from src.domain.orders.events import OrderCreatedEvent
from src.domain.users.entities import User
from src.domain.users.values import Email, HumanName, Telephone
from src.logic.commands.order_commands import (
    AddOrderCommand,
    AddOrderCommandCommandHandler,
    DeleteOrderCommand,
    DeleteOrderCommandCommandHandler,
    TotalAmountDTO,
    UpdateOrderCommand,
    UpdateOrderCommandCommandHandler,
)
from src.logic.commands.user_commands import AddUserCommand, AddUserCommandHandler
from src.logic.events.order_handlers import OrderCreatedEmailEventHandler, OrderCreatedPointIncreaseEventHandler
from src.logic.mediator.base import Mediator
from src.logic.uows.order_uow import SQLAlchemyOrderUnitOfWork
from src.logic.uows.users_uow import SQLAlchemyUsersUnitOfWork


def get_message_bus_with_user_register_handlers():
    mediator = Mediator()
    user_uow = SQLAlchemyUsersUnitOfWork()
    mediator.register_command(AddUserCommand, [AddUserCommandHandler(mediator=mediator, uow=user_uow)])
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


def get_message_bus_with_order_register_handlers():
    mediator = Mediator()
    user_uow = SQLAlchemyOrderUnitOfWork()
    mediator.register_command(AddOrderCommand, [AddOrderCommandCommandHandler(mediator=mediator, uow=user_uow)])
    mediator.register_command(UpdateOrderCommand, [UpdateOrderCommandCommandHandler(mediator=mediator, uow=user_uow)])
    mediator.register_command(DeleteOrderCommand, [DeleteOrderCommandCommandHandler(mediator=mediator, uow=user_uow)])
    mediator.register_event(
        OrderCreatedEvent,
        [OrderCreatedEmailEventHandler(uow=user_uow), OrderCreatedPointIncreaseEventHandler(uow=user_uow)],
    )
    return mediator


async def add_order():
    message_bus = get_message_bus_with_order_register_handlers()
    user = User(
        email=Email("hue@grant.com"),
        first_name=HumanName("Hue"),
        last_name=HumanName("Grant"),
        telephone=Telephone("88005553434"),
    )
    user.id = 13
    order_data = AddOrderCommand(
        total_amount=TotalAmountDTO(
            schedule_id=5,
            point=0,
            promotion_code="sfcsdf6666",
        ),
        time_start="14:00",
        user=user,
    )
    await message_bus.handle_command(order_data)


async def update_order():
    message_bus = get_message_bus_with_order_register_handlers()
    user = User(
        email=Email("hue@grant.com"),
        first_name=HumanName("Hue"),
        last_name=HumanName("Grant"),
        telephone=Telephone("88005553434"),
        date_birthday=date(2024, 12, 6),
    )
    user.id = 13
    order_data = UpdateOrderCommand(user=user, order_id=19, time_start="18:00")
    await message_bus.handle_command(order_data)


async def delete_order():
    message_bus = get_message_bus_with_order_register_handlers()
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
    asyncio.new_event_loop().run_until_complete(add_order())
