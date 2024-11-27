import re

from datetime import date

from pydantic import EmailStr, PositiveInt
from pydantic.functional_validators import field_validator

from src.logic.dto.base_dto import BaseDTO


class UserCreateDTO(BaseDTO):
    email: EmailStr
    first_name: str
    last_name: str
    telephone: str
    password: str
    date_birthday: date | None = None

    @field_validator("password")
    @classmethod
    def name_must_contain_space(cls, password: str) -> str:
        pattern = r"(?=\D*\d)(?=[^A-Z]*[A-Z])(?=[^a-z]*[a-z])[A-Za-z0-9!@#$%^&*()]{8,}$"
        if not re.search(pattern, password):
            raise ValueError("Password need upper and simple letter, 1 digit and 1 symbol with summary length 8")
        return password


class InventoryAddDTO(BaseDTO):
    name: str
    unit: str
    stock_count: PositiveInt


class InventoryUpdateDTO(BaseDTO):
    name: str | None = None
    unit: str | None = None
    stock_count: PositiveInt | None = None


class InventoryDTO(InventoryAddDTO):
    id: int


class MasterAddDTO(BaseDTO):
    description: str
    user_id: int
    services_id: list[int]
