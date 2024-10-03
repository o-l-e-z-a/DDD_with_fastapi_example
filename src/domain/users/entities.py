from dataclasses import dataclass, field
from datetime import date

from src.domain.base.values import CountNumber
from src.domain.users.values import Email, HumanName, Telephone

START_HOUR = 10
END_HOUR = 20
SLOT_DELTA = 1
MINIMUM_BALANCE = 200
LESS_POINT_WARNINGS = "На балансе пользователя меньше баллов"
MORE_POINT_WARNINGS = "На балансе пользователя больше баллов, уменьшили количество"


@dataclass
class User:
    # id: int
    email: Email
    hashed_password: str = field(init=False, default="")
    first_name: HumanName
    last_name: HumanName
    telephone: Telephone
    date_birthday: date | None = None
    # is_active: bool = True
    # is_superuser: bool = False
    # created_at: datetime = field(init=False)
    # updated_at: datetime = field(init=False)


@dataclass
class UserPoint:
    # id: int
    user: User
    count: CountNumber = CountNumber(0)
