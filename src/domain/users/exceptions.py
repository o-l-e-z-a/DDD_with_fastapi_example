from src.domain.base.exceptions import DomainError


class PhoneInvalidError(ValueError, DomainError):
    @property
    def title(self) -> str:
        return "Телефон не валидный"


class EmailInvalidError(ValueError, DomainError):
    @property
    def title(self) -> str:
        return "Почта не валидная"


class NameInvalidError(ValueError, DomainError):
    @property
    def title(self) -> str:
        return "Имя не валидное"
