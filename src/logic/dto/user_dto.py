import re

from datetime import date

from pydantic import EmailStr
from pydantic.functional_validators import field_validator
from pydantic_extra_types.phone_numbers import PhoneNumber

from src.logic.dto.base_dto import BaseDTO


class UserCreateDTO(BaseDTO):
    email: EmailStr
    first_name: str
    last_name: str
    telephone: PhoneNumber
    date_birthday: date | None
    password: str

    @field_validator("password")
    @classmethod
    def name_must_contain_space(cls, password: str) -> str:
        pattern = r"(?=\D*\d)(?=[^A-Z]*[A-Z])(?=[^a-z]*[a-z])[A-Za-z0-9!@#$%^&*()]{8,}$"
        if not re.search(pattern, password):
            raise ValueError("Password need upper and simple letter, 1 digit and 1 symbol with summary length 8")
        return password


class AllUserDTO(BaseDTO):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    telephone: str
