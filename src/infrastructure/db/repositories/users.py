from sqlalchemy import or_, select

from src.domain.users import entities
from src.infrastructure.db.models.users import Users
from src.infrastructure.db.repositories.base import GenericSQLAlchemyQueryRepository, GenericSQLAlchemyRepository
from src.logic.dto.mappers.user_mappers import user_to_detail_dto_mapper
from src.logic.dto.user_dto import UserDetailDTO


class UserRepository(GenericSQLAlchemyRepository[Users, entities.User]):
    model = Users

    async def find_duplicate_user(self, email: str, telephone: str) -> list[entities.User]:
        query = select(self.model).where(or_(self.model.email == email, self.model.telephone == telephone))
        result = await self.session.execute(query)
        return [el.to_domain() for el in result.scalars().all()]


class UserQueryRepository(GenericSQLAlchemyQueryRepository[Users]):
    async def find_one_or_none(self, **filter_by) -> UserDetailDTO | None:
        query = select(Users).filter_by(**filter_by)
        result = await self.session.execute(query)
        scalar = result.scalar_one_or_none()
        return user_to_detail_dto_mapper(scalar) if scalar else None

    async def find_all(self, **filter_by) -> list[UserDetailDTO]:
        query = select(Users).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [user_to_detail_dto_mapper(el) for el in result.scalars().all()]
