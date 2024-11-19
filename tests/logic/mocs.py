from typing import Any, Self, Sequence

from src.domain.base.values import BaseValueObject
from src.domain.users import entities
from src.infrastructure.db.models.base import E, T
from src.infrastructure.db.repositories.users import UserPointRepository, UserRepository
from src.logic.uows.users_uow import SQLAlchemyUsersUnitOfWork


def to_generic_type(element: Any):
    if isinstance(element, BaseValueObject):
        return element.as_generic_type()
    return element


class FakeGenericSQLAlchemyRepository:

    def __init__(self, models: list[E] | None = None) -> None:
        self.models = models if models else []

    async def find_one_or_none(self, **filter_by) -> E | None:
        results = []
        for model in self.models:
            if all(getattr(model, k, None) == v for k, v in filter_by.items()):
                result = model
                if results:
                    raise IndexError
                results.append(result)
        if results:
            return results[0]

    async def find_all(self, **filter_by) -> Sequence[E]:
        results = []
        for model in self.models:
            if all(lambda el: to_generic_type(getattr(model, k, None)) == v for k, v in filter_by.items()):
                result = model
                results.append(result)
        return results

    async def add(self, entity: E) -> None:
        self.models.append(entity)
        return entity

    async def update(self, entity: E) -> None:
        for model in self.models:
            if model.id == entity.id:
                self.models.remove(model)
                self.models.append(entity)
                break
        else:
            raise IndexError
        return entity

    async def delete(self, **filter_by) -> None:
        results = []
        for model in self.models:
            if all(lambda el: to_generic_type(getattr(model, k, None)) == v for k, v in filter_by.items()):
                results.remove(model)
        if results:
            return results[0]


class FakeUserRepository(FakeGenericSQLAlchemyRepository, UserRepository):
    async def find_duplicate_user(self, email: str, telephone: str) -> Sequence[entities.User]:
        results = []
        for model in self.models:
            if to_generic_type(model.email) == email or to_generic_type(model.telephone) == telephone:
                results.append(model)
        return results


class FakeUserPointRepository(FakeGenericSQLAlchemyRepository, UserRepository):

    def check_by_user_id(self, model, **filter_by):
        user_id = filter_by.get('user_id', None)
        if user_id:
            if model.user.id != user_id:
                return False
        return True

    async def find_one_or_none(self, **filter_by) -> entities.UserPoint | None:
        results = []
        for model in self.models:
            if (
                    all(getattr(model, k, None) == v for k, v in filter_by.items() if k != 'user_id')
                    and self.check_by_user_id(model, **filter_by)
            ):
                result = model
                if results:
                    raise IndexError
                results.append(result)
        if results:
            return results[0]


class FakeUsersUnitOfWork(SQLAlchemyUsersUnitOfWork):

    def __init__(self, fake_user_repo, fake_users_statistics) -> None:
        self.committed: bool = False
        self.users = fake_user_repo
        self.user_points = fake_users_statistics

    async def commit(self) -> None:
        self.committed = True

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(*args, **kwargs):
        pass

    async def rollback(self) -> None:
        pass
