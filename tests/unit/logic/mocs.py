from datetime import date
from typing import Any, Self, Sequence

from src.domain.base.values import BaseValueObject
from src.domain.users import entities
from src.infrastructure.db.models.base import E, T
from src.infrastructure.db.repositories.schedules import (
    ConsumablesRepository,
    InventoryRepository,
    MasterRepository,
    ScheduleRepository,
    ServiceRepository,
    SlotRepository,
)
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
        entity.id = len(self.models) + 1
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
    async def find_duplicate_user(self, email: str, telephone: str) -> list[entities.User]:
        results = []
        for model in self.models:
            if to_generic_type(model.email) == email or to_generic_type(model.telephone) == telephone:
                results.append(model)
        return results


class FakeUserPointRepository(FakeGenericSQLAlchemyRepository, UserPointRepository):

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


class FakeScheduleRepository(FakeGenericSQLAlchemyRepository, ScheduleRepository):
    async def get_day_for_master(self, **filter_by) -> list[date]:
        filtered_models = await self.find_all(**filter_by)
        day_set = set()
        for model in filtered_models:
            day_set.add(model.day)
        return sorted(list(day_set))


class FakeInventoryRepository(FakeGenericSQLAlchemyRepository, InventoryRepository):
    pass


class FakeMasterRepository(FakeGenericSQLAlchemyRepository, MasterRepository):
    pass


class FakeServiceRepository(FakeGenericSQLAlchemyRepository, ServiceRepository):
    pass


class FakeSlotRepository(FakeGenericSQLAlchemyRepository, SlotRepository):
    pass


class FakeConsumablesRepository(FakeGenericSQLAlchemyRepository, ConsumablesRepository):
    pass


class FakeGenericUnitOfWork(SQLAlchemyUsersUnitOfWork):

    def __init__(self) -> None:
        self.committed: bool = False

    async def commit(self) -> None:
        self.committed = True

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(*args, **kwargs):
        pass

    async def rollback(self) -> None:
        pass


class FakeUsersUnitOfWork(FakeGenericUnitOfWork):

    def __init__(self, fake_user_repo, fake_user_point_repo) -> None:
        self.users = fake_user_repo
        self.user_points = fake_user_point_repo
        super().__init__()


class FakeScheduleUnitOfWork(FakeGenericUnitOfWork):

    def __init__(
        self,
        fake_schedules_repo,
        fake_slots_repo,
        fake_consumables_repo,
        fake_masters_repo,
        fake_service_repo,
        fake_inventories_repo,
        fake_users_repo,
    ) -> None:
        self.schedules = fake_schedules_repo
        self.slots = fake_slots_repo
        self.consumables = fake_consumables_repo
        self.masters = fake_masters_repo
        self.services = fake_service_repo
        self.inventories = fake_inventories_repo
        self.users = fake_users_repo
        super().__init__()
