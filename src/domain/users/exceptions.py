from src.domain.base.exceptions import DomainError


class PhoneInvalidError(ValueError, DomainError):
    @property
    def title(self) -> str:
        return "Телефон не валидный"


class EmailInvalidError(ValueError, DomainError):
    @property
    def title(self) -> str:
        return "Почта не валидная"


class NameEmptyError(ValueError, DomainError):
    @property
    def title(self) -> str:
        return "Имя слишком короткое"


class NameTooLongError(ValueError, DomainError):
    @property
    def title(self) -> str:
        return "Имя слишком длинное"


class NameInvalidError(ValueError, DomainError):
    @property
    def title(self) -> str:
        return "Имя не валидное"
