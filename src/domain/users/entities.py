from dataclasses import dataclass, field
from datetime import date

from src.domain.base.entities import BaseEntity
from src.domain.base.values import CountNumber
from src.domain.users.values import Email, HumanName, Telephone


@dataclass()
class User(BaseEntity):
    email: Email
    hashed_password: str = field(init=False, default="", compare=False)
    first_name: HumanName
    last_name: HumanName
    telephone: Telephone
    date_birthday: date | None = None

    # is_active: bool = True
    is_admin: bool = False
    # created_at: datetime = field(init=False)
    # updated_at: datetime = field(init=False)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'email': self.email.as_generic_type(),
            'first_name': self.first_name.as_generic_type(),
            'last_name': self.last_name.as_generic_type(),
            'telephone': self.telephone.as_generic_type(),
            'date_birthday': self.date_birthday,
            'is_admin': self.is_admin,
        }
