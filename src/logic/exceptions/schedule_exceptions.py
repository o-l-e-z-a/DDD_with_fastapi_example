from dataclasses import dataclass

from src.logic.exceptions.base_exception import NotFoundLogicException


@dataclass(eq=False)
class InventoryNotFoundLogicException(NotFoundLogicException):
    model: str = "Инвентарь"


@dataclass(eq=False)
class ServiceNotFoundLogicException(NotFoundLogicException):
    model: str = "Сервис"


@dataclass(eq=False)
class SlotNotFoundLogicException(NotFoundLogicException):
    model: str = "Времянное окно"


@dataclass(eq=False)
class MasterNotFoundLogicException(NotFoundLogicException):
    model: str = "Мастер"


@dataclass(eq=False)
class ScheduleNotFoundLogicException(NotFoundLogicException):
    model: str = "Расписание"


@dataclass(eq=False)
class OrderNotFoundLogicException(NotFoundLogicException):
    model: str = 'Заказ'
