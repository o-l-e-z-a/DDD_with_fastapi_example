import re

from dataclasses import dataclass

from src.domain.base.exceptions import NameEmptyError, NameTooLongError
from src.domain.base.values import BaseValueObject
from src.domain.users.exceptions import EmailInvalidError, NameInvalidError, PhoneInvalidError

MAX_HUMAN_NAME_LENGTH = 16
NAME_REGEX = re.compile(r"^[а-яА-Яa-zA-Z]+$")
RU_PHONE_NUMBER_REGEX = re.compile(r"(^8|7|\+7)((\d{10})|(\s\(\d{3}\)\s\d{3}\s\d{2}\s\d{2}))")
EMAIL_REGEX = re.compile(
    r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9]"
    r"(?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$"
)


@dataclass(frozen=True)
class Telephone(BaseValueObject[str]):
    value: str

    def validate(self):
        if not RU_PHONE_NUMBER_REGEX.match(self.value):
            raise PhoneInvalidError()


@dataclass(frozen=True)
class Email(BaseValueObject[str]):
    value: str

    def validate(self):
        if not EMAIL_REGEX.match(self.value):
            raise EmailInvalidError()


@dataclass(frozen=True)
class HumanName(BaseValueObject[str]):
    value: str

    def validate(self):
        if len(self.value) > MAX_HUMAN_NAME_LENGTH:
            raise NameTooLongError()
        if not self.value:
            raise NameEmptyError()
        if not NAME_REGEX.match(self.value):
            raise NameInvalidError()
