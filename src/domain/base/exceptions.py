from dataclasses import dataclass
from typing import Any


@dataclass(eq=False)
class DomainException(Exception):
    @property
    def title(self) -> str:
        return "Произошла ошибка в домене"


@dataclass(eq=False)
class BaseValueObjectException(DomainException, ValueError):
    value: Any


class IntegerException(BaseValueObjectException):
    @property
    def title(self) -> str:
        return f'Число {self.value} не целое'


class PositiveNumberException(BaseValueObjectException):
    @property
    def title(self) -> str:
        return f'Число {self.value} меньше или равно нулю'


class CountNumberException(BaseValueObjectException):
    @property
    def title(self) -> str:
        return f'Число {self.value} меньше нуля'


class EmptyNameException(BaseValueObjectException):
    @property
    def title(self) -> str:
        return f'Имя "{self.value}" слишком короткое'


class NameTooLongException(BaseValueObjectException):
    @property
    def title(self) -> str:
        return f'Имя "{self.value}" слишком длинное'
