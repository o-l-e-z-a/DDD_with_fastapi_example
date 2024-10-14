from abc import ABC, abstractmethod
from typing import Generic, Sequence, Type, TypeVar

from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class AbstractRepository(ABC):
    @abstractmethod
    async def add(self): ...

    @abstractmethod
    async def find_all(self): ...


class SQLAlchemyRepository(Generic[T], AbstractRepository):
    model: Type[T]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_one_or_none(self, **filter_by) -> T | None:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def find_all(self, **filter_by) -> Sequence[T]:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def add(self, **data) -> int:
        query = insert(self.model).values(**data).returning(self.model.id)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def update(self, model_item: T, **data) -> T:
        for name, value in data.items():
            setattr(model_item, name, value)
        await self.session.refresh(model_item)
        return model_item

    async def delete(self, **filter_by):
        query = delete(self.model).filter_by(**filter_by)
        await self.session.execute(query)

    async def add_bulk(self, *data):
        query = insert(self.model).values(*data).returning(self.model.id)
        result = await self.session.execute(query)
        return result.scalars().first()
