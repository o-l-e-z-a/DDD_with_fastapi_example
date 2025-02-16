from sqlalchemy import or_, select

from src.domain.users import entities
from src.infrastructure.db.models.users import Users
from src.infrastructure.db.repositories.base import GenericSQLAlchemyQueryRepository, GenericSQLAlchemyRepository
from src.logic.dto.user_dto import UserDetailDTO


class UserRepository(GenericSQLAlchemyRepository[Users, entities.User]):
    model = Users

    async def find_duplicate_user(self, email: str, telephone: str) -> list[entities.User]:
        query = select(self.model).where(or_(self.model.email == email, self.model.telephone == telephone))
        result = await self.session.execute(query)
        return [el.to_domain() for el in result.scalars().all()]


class UserQueryRepository(GenericSQLAlchemyQueryRepository[Users]):
    async def find_all(self, **filter_by) -> list[UserDetailDTO]:
        query = select(Users).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [
            UserDetailDTO(
                id=el.id,
                email=el.email,
                first_name=el.first_name,
                last_name=el.last_name,
                telephone=el.telephone,
                is_admin=el.is_superuser,
                date_birthday=el.date_birthday,
            )
            for el in result.scalars().all()
        ]
