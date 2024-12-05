from dataclasses import dataclass

from src.logic.exceptions.base_exception import NotFoundLogicException


@dataclass(eq=False)
class UserNotFoundLogicException(NotFoundLogicException):
    model: str = 'Пользователь'


@dataclass(eq=False)
class UserPointNotFoundLogicException(NotFoundLogicException):
    model: str = 'Баллы пользователя'
