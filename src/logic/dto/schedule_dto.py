from dataclasses import dataclass
from datetime import date, time, datetime

from src.logic.dto.base_dto import BaseDTO
from src.logic.dto.user_dto import UserDetailDTO


@dataclass(frozen=True)
class ServiceDTO(BaseDTO):
    id: int
    name: str
    description: str
    price: int


@dataclass(frozen=True)
class MasterDetailDTO(BaseDTO):
    id: int
    description: str
    user: UserDetailDTO
    services: list[ServiceDTO]


@dataclass(frozen=True)
class ScheduleShortDTO(BaseDTO):
    id: int
    day: date


@dataclass(frozen=True)
class ScheduleDetailDTO(BaseDTO):
    id: int
    day: date
    master: MasterDetailDTO


@dataclass(frozen=True)
class SlotDetailDTO(BaseDTO):
    id: int
    time_start: time
    schedule: ScheduleDetailDTO


@dataclass(frozen=True)
class OrderDetailDTO(BaseDTO):
    id: int
    date_add: datetime
    service: ServiceDTO
    user: UserDetailDTO
    slot: SlotDetailDTO
    photo_before_path: str | None
    photo_after_path: str | None


@dataclass(frozen=True)
class ClientOrderDetailDTO(BaseDTO):
    id: int
    date_add: datetime
    service: ServiceDTO
    slot: SlotDetailDTO
    photo_before_path: str | None
    photo_after_path: str | None


@dataclass(frozen=True)
class MasterReportDTO(BaseDTO):
    id: int
    last_name: str
    first_name: str
    total_count: int
    total_sum: int


@dataclass(frozen=True)
class ServiceReportDTO(BaseDTO):
    id: int
    name: str
    price: int
    total_count: int
    total_sum: int
