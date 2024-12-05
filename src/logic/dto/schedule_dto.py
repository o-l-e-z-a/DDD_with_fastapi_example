from datetime import date

from pydantic import PositiveInt

from src.logic.dto.base_dto import BaseDTO


class InventoryAddDTO(BaseDTO):
    name: str
    unit: str
    stock_count: PositiveInt


class InventoryUpdateDTO(BaseDTO):
    inventory_id: int
    name: str | None = None
    unit: str | None = None
    stock_count: PositiveInt | None = None


class InventoryDTO(InventoryAddDTO):
    id: int


class MasterAddDTO(BaseDTO):
    description: str
    user_id: int
    services_id: list[int]


class ScheduleAddDTO(BaseDTO):
    day: date
    service_id: int
    master_id: int
