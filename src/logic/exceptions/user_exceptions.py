from dataclasses import dataclass

from src.logic.exceptions.base_exception import LogicException, NotFoundLogicException


@dataclass(eq=False)
class UserAlreadyExistsLogicException(LogicException):
    email: str
    telephone: str

    @property
    def title(self) -> str:
        return f"Пользователь c email: {self.email} или номером: {self.telephone} - существует"


@dataclass(eq=False)
class UserNotFoundLogicException(NotFoundLogicException):
    model: str = "Пользователь"


@dataclass(eq=False)
class IncorrectEmailOrPasswordLogicException(LogicException):
    @property
    def title(self) -> str:
        return "Неверная почта или пароль"
