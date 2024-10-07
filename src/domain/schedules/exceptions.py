from src.domain.base.exceptions import DomainError


class SlotOccupiedError(ValueError, DomainError):
    @property
    def title(self) -> str:
        return "Времянное окно уже занято"


class SlotInvalidError(ValueError, DomainError):
    @property
    def title(self) -> str:
        return "Времянное окно уже занято"
