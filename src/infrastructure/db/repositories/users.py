from typing import Sequence

from sqlalchemy import or_, select
from sqlalchemy.orm import joinedload

from src.infrastructure.db.models.users import UserPoint, Users
from src.infrastructure.db.repositories.base import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository[Users]):
    model = Users

    async def find_duplicate_user(self, email: str, telephone: str) -> Sequence[Users]:
        query = select(self.model).where(or_(self.model.email == email, self.model.telephone == telephone))
        result = await self.session.execute(query)
        return result.scalars().all()


class UserPointRepository(SQLAlchemyRepository[UserPoint]):
    model = UserPoint

    async def find_one_or_none(self, **filter_by) -> UserPoint | None:
        query = select(self.model).options(joinedload(self.model.user)).filter_by(**filter_by)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
