from dataclasses import dataclass
from typing import ClassVar


@dataclass(eq=False)
class AppError(Exception):
    """Base Error."""

    status: ClassVar[int] = 500

    @property
    def title(self) -> str:
        return "An app error occurred"


class DomainError(AppError):
    """Base Domain Error."""

    @property
    def title(self) -> str:
        return "A domain error occurred"


class IntegerError(ValueError, DomainError):
    @property
    def title(self) -> str:
        return "Число не целое"


class PositiveNumberError(ValueError, DomainError):
    @property
    def title(self) -> str:
        return "Число меньше или равно нулю"


class CountNumberError(ValueError, DomainError):
    @property
    def title(self) -> str:
        return "Число меньше нуля"
