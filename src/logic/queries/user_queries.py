from dataclasses import dataclass

from pydantic import PositiveInt

from src.infrastructure.db.uows.users_uow import SQLAlchemyUsersQueryUnitOfWork
from src.logic.dto.user_dto import UserDetailDTO
from src.logic.queries.base import BaseQuery, QueryHandler


class GetUserByIdQuery(BaseQuery):
    user_id: PositiveInt


@dataclass(frozen=True)
class GetUserByIdQueryHandler(QueryHandler[GetUserByIdQuery, UserDetailDTO | None]):
    uow: SQLAlchemyUsersQueryUnitOfWork

    async def handle(self, query: GetUserByIdQuery) -> UserDetailDTO | None:
        async with self.uow:
            results = await self.uow.users.find_one_or_none(id=query.user_id)
        return results
