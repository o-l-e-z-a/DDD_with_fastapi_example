from __future__ import annotations

from datetime import datetime
from typing import Annotated, Generic, Self, TypeVar

from sqlalchemy import BigInteger, func
from sqlalchemy.orm import DeclarativeBase, mapped_column

from src.domain.base.entities import BaseEntity

E = TypeVar("E", bound=BaseEntity)

int_pk = Annotated[int, mapped_column(BigInteger, primary_key=True)]
created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[datetime, mapped_column(server_default=func.now(), onupdate=datetime.now)]
str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]
str_null_true = Annotated[str, mapped_column(nullable=True)]
str_255 = Annotated[str, 255]


def get_child_join_and_level(with_join: bool = False, child_level: int = 0):
    if with_join and child_level > 1:
        child_level -= 1
        with_join_to_child = True
    else:
        with_join_to_child = False
    return with_join_to_child, child_level


class Base(DeclarativeBase, Generic[E]):
    repr_cols_num = 3
    repr_cols: tuple = ()

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__._columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col} = {getattr(self, col)}")
        return f'<{self.__class__.__name__} {", ".join(cols)}>'

    @classmethod
    def from_entity(cls, entity: E) -> Self: ...

    def to_domain(self, with_join: bool = False, child_level: int = 0) -> E: ...


T = TypeVar("T", bound=Base)
