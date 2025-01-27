from dataclasses import dataclass
from datetime import date

from pydantic import EmailStr

from src.domain.users.entities import User, UserPoint
from src.domain.users.values import Email, HumanName, Telephone
from src.logic.commands.base import BaseCommand, CommandHandler
from src.logic.exceptions.user_exceptions import UserAlreadyExistsLogicException
from src.logic.services.users_service import get_password_hash
from src.logic.uows.users_uow import SQLAlchemyUsersUnitOfWork


class CreateUserCommand(BaseCommand):
    email: EmailStr
    first_name: str
    last_name: str
    telephone: str
    password: str
    date_birthday: date | None = None


@dataclass(frozen=True)
class CreateUserCommandHandler(CommandHandler[CreateUserCommand, User]):
    uow: SQLAlchemyUsersUnitOfWork

    async def handle(self, command: CreateUserCommand) -> User:
        async with self.uow:
            existing_user = await self.uow.users.find_duplicate_user(email=command.email, telephone=command.telephone)
            if existing_user:
                raise UserAlreadyExistsLogicException(email=command.email, telephone=command.telephone)
            password_hash = get_password_hash(command.password)
            user = User(
                email=Email(command.email),
                first_name=HumanName(command.first_name),
                last_name=HumanName(command.last_name),
                telephone=Telephone(command.telephone),
                date_birthday=command.date_birthday,
            )
            user.hashed_password = password_hash
            user_from_repo = await self.uow.users.add(entity=user)
            user_point = UserPoint(user=user_from_repo)
            await self.uow.user_points.add(entity=user_point)
            await self.uow.commit()
            # TODO! add to the all command handlers
            events = user.pull_events() + user_point.pull_events()
            print(events)
            await self.mediator.publish(events)
            return user_from_repo
