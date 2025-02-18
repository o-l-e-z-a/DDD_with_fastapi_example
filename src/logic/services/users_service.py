from passlib.context import CryptContext

from src.domain.users.entities import User
from src.logic.dto.user_dto import UserLoginDTO
from src.logic.exceptions.user_exceptions import (
    IncorrectEmailOrPasswordLogicException,
)
from src.infrastructure.db.uows.users_uow import SQLAlchemyUsersUnitOfWork

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


class UserService:
    def __init__(self, uow: SQLAlchemyUsersUnitOfWork):
        self.uow = uow


    async def check_login_and_verify_password(self, user_login_data: UserLoginDTO):
        async with self.uow:
            user = await self.uow.users.find_one_or_none(email=user_login_data.email)
            if not (user and verify_password(user_login_data.password, user.hashed_password)):
                raise IncorrectEmailOrPasswordLogicException()
            return user

    # async def get_user_point(self, user: User) -> UserPoint | None:
    #     async with self.uow:
    #         user_point = await self.uow.user_points.find_one_or_none(user_id=user.id)
    #         if not user_point:
    #             raise UserPointNotFoundLogicException(id=user.id)
    #     return user_point

    async def get_user_by_id(self, user_id: int) -> User | None:
        async with self.uow:
            user = await self.uow.users.find_one_or_none(id=user_id)
        return user
