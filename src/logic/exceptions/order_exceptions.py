from dataclasses import dataclass

from src.logic.exceptions.base_exception import NotFoundLogicException, LogicException


@dataclass(eq=False)
class NotUserOrderLogicException(LogicException):
    @property
    def title(self) -> str:
        return "Ошибка логики работы приложения"


@dataclass(eq=False)
class OrderNotFoundLogicException(NotFoundLogicException):
    model: str = 'Заказ'


@dataclass(eq=False)
class PromotionNotFoundLogicException(NotFoundLogicException):
    model: str = 'Промокод'
