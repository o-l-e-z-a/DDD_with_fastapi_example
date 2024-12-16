from passlib.context import CryptContext

from src.domain.users.entities import User, UserPoint
from src.domain.users.values import Email, HumanName, Telephone
from src.logic.dto.user_dto import UserCreateDTO, UserLoginDTO
from src.logic.exceptions.user_exceptions import (
    IncorrectEmailOrPasswordLogicException,
    UserAlreadyExistsLogicException,
    UserPointNotFoundLogicException,
)
from src.logic.uows.users_uow import SQLAlchemyUsersUnitOfWork

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


class UserService:
    def __init__(self, uow: SQLAlchemyUsersUnitOfWork):
        self.uow = uow

    async def add_user(self, user_data: UserCreateDTO) -> User:
        async with self.uow:
            existing_user = await self.uow.users.find_duplicate_user(
                email=user_data.email, telephone=user_data.telephone
            )
            if existing_user:
                raise UserAlreadyExistsLogicException(email=user_data.email, telephone=user_data.telephone)
            password_hash = get_password_hash(user_data.password)
            user = User(
                email=Email(user_data.email),
                first_name=HumanName(user_data.first_name),
                last_name=HumanName(user_data.last_name),
                telephone=Telephone(user_data.telephone),
                date_birthday=user_data.date_birthday,
            )
            user.hashed_password = password_hash
            user_from_repo = await self.uow.users.add(entity=user)
            user_point = UserPoint(user=user_from_repo)
            await self.uow.user_points.add(entity=user_point)
            await self.uow.commit()
            return user_from_repo

    async def check_login_and_verify_password(self, user_login_data: UserLoginDTO):
        async with self.uow:
            user = await self.uow.users.find_one_or_none(email=user_login_data.email)
            if not (user and verify_password(user_login_data.password, user.hashed_password)):
                raise IncorrectEmailOrPasswordLogicException()
            return user

    async def get_user_point(self, user: User) -> UserPoint | None:
        async with self.uow:
            user_point = await self.uow.user_points.find_one_or_none(user_id=user.id)
            if not user_point:
                raise UserPointNotFoundLogicException(id=user.id)
        return user_point

    async def get_user_by_id(self, user_id: int) -> User | None:
        async with self.uow:
            user = await self.uow.users.find_one_or_none(id=user_id)
        return user
