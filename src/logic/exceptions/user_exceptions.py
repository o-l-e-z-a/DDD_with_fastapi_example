from dataclasses import dataclass

from src.logic.exceptions.base_exception import NotFoundLogicException, LogicException


@dataclass(eq=False)
class UserAlreadyExistsLogicException(LogicException):
    email: str
    telephone: str

    @property
    def title(self) -> str:
        return f"Пользователь c email: {self.email} или номером: {self.telephone} существует"


@dataclass(eq=False)
class UserNotFoundLogicException(NotFoundLogicException):
    model: str = 'Пользователь'


@dataclass(eq=False)
class UserPointNotFoundLogicException(NotFoundLogicException):
    model: str = 'Баллы пользователя'


@dataclass(eq=False)
class IncorrectEmailOrPasswordLogicException(LogicException):

    @property
    def title(self) -> str:
        return f"Неверная почта или пароль"
