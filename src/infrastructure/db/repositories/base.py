from abc import ABC
from typing import Generic, Sequence, Type

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.models.base import E, T


class AbstractRepository(ABC): ...


class GenericSQLAlchemyRepository(Generic[T, E], AbstractRepository):
    model: Type[T]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_one_or_none(self, **filter_by) -> E | None:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        scalar = result.scalar_one_or_none()
        return scalar.to_domain() if scalar else None

    async def find_all(self, **filter_by) -> Sequence[E]:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [el.to_domain() for el in result.scalars().all()]

    async def add(self, entity: E) -> None:
        model = self.model.from_entity(entity)
        self.session.add(model)

    async def update(self, entity: E) -> None:
        model = self.model.from_entity(entity)
        await self.session.merge(model)

    async def delete(self, **filter_by) -> None:
        query = delete(self.model).filter_by(**filter_by)
        await self.session.execute(query)

    # async def add_bulk(self, data: Sequence[BaseEntity]) -> None:
    #     query = insert(self.model).values(*data).returning(self.model.id)
    #     result = await self.session.execute(query)
    #     return result.scalars().first()
