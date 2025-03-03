from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from src.domain.base.exceptions import (
    CountNumberException,
    EmptyNameException,
    IntegerException,
    NameTooLongException,
    PositiveNumberException,
)

VT = TypeVar("VT", bound=Any)

MAX_NAME_LENGTH = 50


@dataclass(frozen=True)
class BaseValueObject(ABC, Generic[VT]):
    value: VT

    def __post_init__(self):
        self.validate()

    def as_generic_type(self) -> VT:
        return self.value

    @abstractmethod
    def validate(self): ...


class BaseIntValueObject(BaseValueObject[int]):
    value: int

    def validate(self):
        if not isinstance(self.value, int):
            raise IntegerException(value=self.value)

    def __bool__(self):
        return self.value > 0

    def __eq__(self, other):
        return self.value == other

    def __lt__(self, other):
        return self.value < other

    def __ge__(self, other):
        return self.value > other

    def __add__(self, other):
        return self.value + other

    def __sub__(self, other):
        return self.value - other

    def __mul__(self, other):
        return self.value * other

    def __truediv__(self, other):
        return self.value / other

    def __radd__(self, other):
        return self + other

    def __rsub__(self, other):
        return other - self.value

    def __rmul__(self, other):
        return self * other

    def __rtruediv__(self, other):
        return other / self.value


@dataclass(frozen=True)
class PositiveIntNumber(BaseIntValueObject):
    def validate(self):
        super().validate()
        if self.value <= 0:
            raise PositiveNumberException(self.value)


@dataclass(frozen=True)
class CountNumber(BaseIntValueObject):
    def validate(self):
        super().validate()
        if self.value < 0:
            raise CountNumberException(self.value)


@dataclass(frozen=True)
class Name(BaseValueObject[str]):
    value: str

    def validate(self):
        if len(self.value) > MAX_NAME_LENGTH:
            raise NameTooLongException(self.value)
        if not self.value:
            raise EmptyNameException(self.value)
