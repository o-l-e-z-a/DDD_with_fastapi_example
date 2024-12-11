from dataclasses import dataclass

from src.domain.base.entities import BaseEntity


@dataclass(eq=False)
class BDException(Exception):
    entity: BaseEntity
    detail: str

    @property
    def title(self) -> str:
        return "Ошибка работы БД"


class InsertException(BDException):
    @property
    def title(self) -> str:
        return f"Произошла ошибка добавления сущности {self.entity}, сообщение: {self.detail}"


class UpdateException(BDException):
    @property
    def title(self) -> str:
        return f"Произошла ошибка изменения сущности {self.entity}, сообщение: {self.detail}"


class DeleteException(BDException):
    @property
    def title(self) -> str:
        return f"Произошла ошибка изменения сущности {self.entity}, сообщение: {self.detail}"
