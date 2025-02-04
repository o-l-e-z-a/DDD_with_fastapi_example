from dataclasses import dataclass

from src.domain.base.exceptions import BaseValueObjectException, DomainException


@dataclass(eq=False)
class SlotOccupiedException(ValueError, DomainException):
    @property
    def title(self) -> str:
        return "Времянное окно некорректно или уже занято"


@dataclass(eq=False)
class SlotServiceInvalidException(ValueError, DomainException):
    @property
    def title(self) -> str:
        return "Времянное окно не подходит для данной услуги"


@dataclass(eq=False)
class SlotInvalidException(BaseValueObjectException):
    @property
    def title(self) -> str:
        return f'Времянное окно "{self.value}" имеет неверный формат'
