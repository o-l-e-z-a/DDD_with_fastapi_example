from abc import ABC
from typing import Generic, Type

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.exceptions import InsertException, UpdateException
from src.infrastructure.db.models.base import E, T


class BaseRepository(ABC): ...


class BaseQueryRepository(ABC): ...


class GenericSQLAlchemyQueryRepository(Generic[T], BaseQueryRepository):
    model: Type[T]

    def __init__(self, session: AsyncSession):
        self.session = session


class GenericSQLAlchemyRepository(Generic[T, E], BaseRepository):
    model: Type[T]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_one_or_none(self, **filter_by) -> E | None:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        scalar = result.scalar_one_or_none()
        return scalar.to_domain() if scalar else None

    async def find_all(self, **filter_by) -> list[E]:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [el.to_domain() for el in result.scalars().all()]

    async def add(self, entity: E) -> E:
        model = self.model.from_entity(entity)
        self.session.add(model)
        try:
            await self.session.flush()
        except IntegrityError as err:
            raise InsertException(entity=entity, detail=str(err.args))
        return model.to_domain()

    async def update(self, entity: E) -> E:
        model = self.model.from_entity(entity)
        await self.session.merge(model)
        try:
            await self.session.flush()
        except IntegrityError as err:
            raise UpdateException(entity=entity, detail=str(err.args))
        return model.to_domain()

    async def delete(self, **filter_by) -> None:
        query = delete(self.model).filter_by(**filter_by)
        await self.session.execute(query)
