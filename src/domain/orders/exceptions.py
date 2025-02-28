from dataclasses import dataclass

from src.domain.base.exceptions import DomainException


@dataclass(eq=False)
class OrderIsPayedException(DomainException):
    @property
    def title(self) -> str:
        return "Заказ уже оплачен"
