from dataclasses import dataclass

from src.domain.base.exceptions import DomainException, BaseValueObjectException


@dataclass(eq=False)
class SlotOccupiedException(ValueError, DomainException):
    @property
    def title(self) -> str:
        return "Времянное окно уже занято"


@dataclass(eq=False)
class SlotInvalidException(BaseValueObjectException):
    @property
    def title(self) -> str:
        return f'Времянное окно "{self.value}" имеет неверный формат'
