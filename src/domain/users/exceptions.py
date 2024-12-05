from src.domain.base.exceptions import BaseValueObjectException


class PhoneInvalidException(BaseValueObjectException):
    @property
    def title(self) -> str:
        return f'Телефон "{self.value}" не валидный'


class EmailInvalidException(BaseValueObjectException):
    @property
    def title(self) -> str:
        return f'Почта "{self.value}" не валидная'


class NameInvalidException(BaseValueObjectException):
    @property
    def title(self) -> str:
        return f'Имя "{self.value}" не валидное'
