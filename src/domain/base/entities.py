from abc import ABC
from dataclasses import dataclass, field


@dataclass
class BaseEntity(ABC):
    id: int = field(init=False, hash=False, repr=False, compare=False)

    def to_dict(self) -> dict:
        ...
