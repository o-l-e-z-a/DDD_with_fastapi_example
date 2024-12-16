import re

from datetime import date

from pydantic import EmailStr
from pydantic.functional_validators import field_validator

from src.presentation.api.base.base_schema import BaseSchema


class UserLoginSchema(BaseSchema):
    email: EmailStr
    password: str


class UserCreateSchema(BaseSchema):
    email: EmailStr
    first_name: str
    last_name: str
    telephone: str
    date_birthday: date | None
    password: str

    @field_validator("password")
    @classmethod
    def name_must_contain_space(cls, password: str) -> str:
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[^\w\s]).{8,}"
        if not re.search(pattern, password):
            raise ValueError(
                "Password need upper and simple letter, 1 digit and 1 symbol with minimal summary length 8"
            )
        return password


class AllUserSchema(BaseSchema):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    telephone: str
    is_admin: bool
    date_birthday: date | None

    # @computed_field
    # @property
    # def fio(self) -> str:
    #     return f'{self.last_name} {self.first_name}'


class UserPointSchema(BaseSchema):
    count: int
