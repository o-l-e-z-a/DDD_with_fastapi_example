from dataclasses import dataclass
from datetime import date

from passlib.context import CryptContext
from pydantic import EmailStr

from src.domain.users.entities import User
from src.domain.users.values import Email, HumanName, Telephone
from src.infrastructure.db.uows.users_uow import SQLAlchemyUsersUnitOfWork
from src.infrastructure.logger_adapter.logger import init_logger
from src.logic.commands.base import BaseCommand, CommandHandler
from src.logic.events.user_events import UserCreatedEvent
from src.logic.exceptions.user_exceptions import IncorrectEmailOrPasswordLogicException, UserAlreadyExistsLogicException

logger = init_logger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


class AddUserCommand(BaseCommand):
    email: EmailStr
    first_name: str
    last_name: str
    telephone: str
    password: str
    date_birthday: date | None = None


@dataclass(frozen=True)
class AddUserCommandHandler(CommandHandler[AddUserCommand, User]):
    uow: SQLAlchemyUsersUnitOfWork

    async def handle(self, command: AddUserCommand) -> User:
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
            await self.uow.commit()
        events = user.pull_events()
        created_event = UserCreatedEvent(
            user_id=user_from_repo.id,
            email=user_from_repo.email.as_generic_type(),
            first_name=user_from_repo.first_name.as_generic_type(),
            last_name=user_from_repo.last_name.as_generic_type(),
        )
        events.append(created_event)
        await self.mediator.publish(events)
        return user_from_repo


class VerifyUserCredentialsCommand(BaseCommand):
    email: EmailStr
    password: str


@dataclass(frozen=True)
class VerifyUserCredentialsCommandHandler(CommandHandler[VerifyUserCredentialsCommand, User]):
    uow: SQLAlchemyUsersUnitOfWork

    async def handle(self, command: VerifyUserCredentialsCommand) -> User:
        async with self.uow:
            user = await self.uow.users.find_one_or_none(email=command.email)
            if not (user and verify_password(command.password, user.hashed_password)):
                raise IncorrectEmailOrPasswordLogicException()
            return user
