from dataclasses import dataclass

from src.logic.exceptions.base_exception import NotFoundLogicException, LogicException


@dataclass(eq=False)
class NotUserOrderLogicException(LogicException):
    @property
    def title(self) -> str:
        return "Пользователь не может редактировать чужой заказ"


@dataclass(eq=False)
class OrderNotFoundLogicException(NotFoundLogicException):
    model: str = 'Заказ'


@dataclass(eq=False)
class PromotionNotFoundLogicException(NotFoundLogicException):
    model: str = 'Промокод'
