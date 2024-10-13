from datetime import datetime
from typing import Annotated

from sqlalchemy import BigInteger, func
from sqlalchemy.orm import DeclarativeBase, declared_attr, mapped_column


class Base(DeclarativeBase):
    repr_cols_num = 3
    repr_cols: tuple = ()

    @declared_attr
    def __tablename__(self) -> str:
        return self.__name__.lower()

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__._columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col} = {getattr(self, col)}")
        return f'<{self.__class__.__name__} {", ".join(cols)}>'


int_pk = Annotated[int, mapped_column(BigInteger, primary_key=True)]
created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[datetime, mapped_column(server_default=func.now(), onupdate=datetime.now)]
str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]
str_null_true = Annotated[str, mapped_column(nullable=True)]
str_255 = Annotated[str, 255]
