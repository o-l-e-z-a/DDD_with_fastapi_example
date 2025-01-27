import asyncio

from src.logic.commands.user_commands import CreateUserCommand, CreateUserCommandHandler
from src.logic.mediator.base import Mediator
from src.logic.uows.users_uow import SQLAlchemyUsersUnitOfWork


def get_message_bus_with_user_register_handlers():
    mediator = Mediator()
    user_uow = SQLAlchemyUsersUnitOfWork()
    mediator.register_command(CreateUserCommand, [CreateUserCommandHandler(mediator=mediator, uow=user_uow)])
    return mediator


async def main():
    message_bus = get_message_bus_with_user_register_handlers()
    await message_bus.handle_command(
        CreateUserCommand(
            email="safas@wsefg.com",
            first_name="sad",
            last_name="asdas",
            telephone="880055534323",
            password="asdas@13H",
        )
    )


if __name__ == "__main__":
    asyncio.new_event_loop().run_until_complete(main())
