from dataclasses import dataclass

from src.domain.base.values import BaseValueObject


@dataclass(frozen=True)
class MessageType(BaseValueObject[str]):
    value: str

    def validate(self):
        return True

    @property
    def module_name(self) -> str:
        without_class_name = self.value.split(".")[:-1]
        return ".".join(without_class_name)

    @property
    def class_name(self) -> str:
        return self.value.split(".")[-1]

    def __str__(self) -> str:
        return self.value
