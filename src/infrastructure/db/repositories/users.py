from sqlalchemy import or_, select
from sqlalchemy.orm import joinedload

from src.domain.users import entities
from src.infrastructure.db.models.users import UserPoint, Users
from src.infrastructure.db.repositories.base import GenericSQLAlchemyRepository


class UserRepository(GenericSQLAlchemyRepository[Users, entities.User]):
    model = Users

    async def find_duplicate_user(self, email: str, telephone: str) -> list[entities.User]:
        query = select(self.model).where(or_(self.model.email == email, self.model.telephone == telephone))
        result = await self.session.execute(query)
        return [el.to_domain() for el in result.scalars().all()]


class UserPointRepository(GenericSQLAlchemyRepository[UserPoint, entities.UserPoint]):
    model = UserPoint

    async def find_one_or_none(self, **filter_by) -> entities.UserPoint | None:
        query = select(self.model).options(joinedload(self.model.user)).filter_by(**filter_by)
        result = await self.session.execute(query)
        scalar = result.scalar_one_or_none()
        return scalar.to_domain() if scalar else None
