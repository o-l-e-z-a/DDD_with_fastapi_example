from dataclasses import dataclass
from datetime import date
from tempfile import SpooledTemporaryFile
from typing import Annotated, BinaryIO

from pydantic import Field

from src.logic.dto.base_dto import BaseDTO

int_ge_0 = Annotated[int, Field(ge=0)]
slot_type = Annotated[str, Field(pattern=r"^(?:[01][0-9]|2?[0-3]):[0-5]\d$")]


@dataclass(frozen=True)
class TotalAmountDTO(BaseDTO):
    schedule_id: int
    point: int_ge_0 | None = 0
    promotion_code: str | None = "0"

