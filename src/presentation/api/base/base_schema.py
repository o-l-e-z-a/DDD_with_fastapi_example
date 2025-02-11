from typing import Annotated

from pydantic import BaseModel, Field


int_ge_0 = Annotated[int, Field(ge=0)]


class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
