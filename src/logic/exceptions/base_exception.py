from dataclasses import dataclass


@dataclass(eq=False)
class LogicException(Exception):

    @property
    def title(self) -> str:
        return "Ошибка логики работы приложения"


@dataclass(eq=False)
class NotFoundLogicException(LogicException):
    id: int | list[int]
    model: str

    @property
    def title(self) -> str:
        id_str = f"{','.join(map(str, self.id))}" if isinstance(self.id, list) else self.id
        return f"{self.model} с id {id_str} не был найден"
