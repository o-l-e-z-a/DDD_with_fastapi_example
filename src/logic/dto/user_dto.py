from dataclasses import dataclass
from datetime import date

from src.logic.dto.base_dto import BaseDTO


@dataclass(frozen=True)
class UserLoginDTO(BaseDTO):
    email: str
    password: str


@dataclass(frozen=True)
class UserDetailDTO(BaseDTO):
    id: int
    email: str
    first_name: str
    last_name: str
    telephone: str
    is_admin: bool
    date_birthday: date | None

    @property
    def full_name(self):
        return f'{self.last_name} {self.first_name}'