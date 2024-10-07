import re

from datetime import time

from src.domain.base.values import BaseValueObject
from src.domain.schedules.exceptions import SlotInvalidError

SLOT_TIME_REGEX = re.compile(r"^(?:[01][0-9]|2?[0-3]):[0-5]\d$")
START_HOUR = 10
END_HOUR = 20
SLOT_DELTA = 1


class SlotTime(BaseValueObject[str]):
    value: str

    def validate(self):
        if not SLOT_TIME_REGEX.match(self.value):
            raise SlotInvalidError()

    def __gt__(self, other):
        return time.fromisoformat(self.value) > time.fromisoformat(other.value)

    def __lt__(self, other):
        return time.fromisoformat(self.value) < time.fromisoformat(other.value)
