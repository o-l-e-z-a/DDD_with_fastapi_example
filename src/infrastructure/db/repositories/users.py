from typing import Sequence

from sqlalchemy import or_, select

from src.infrastructure.db.models.users import Users
from src.infrastructure.db.repositories.base import SQLAlchemyRepository


class UserDAO(SQLAlchemyRepository[Users]):
    model = Users

    async def find_duplicate_user(self, email: str, telephone: str) -> Sequence[Users]:
        query = select(self.model).where(or_(self.model.email == email, self.model.telephone == telephone))
        result = await self.session.execute(query)
        return result.scalars().all()
