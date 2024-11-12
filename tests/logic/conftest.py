import pytest

from src.logic.dto.user_dto import UserCreateDTO
from src.logic.services.users_service import UserService
from tests.domain.conftest import *

from .mocs import FakeUserPointRepository, FakeUserRepository, FakeUsersUnitOfWork


@pytest.fixture()
def user_service_with_data(user_ivanov, ivanov_user_point, user_petrov, petrov_user_point):
    user_repo = FakeUserRepository(models=[user_ivanov, user_petrov])
    user_point_repo = FakeUserPointRepository(models=[ivanov_user_point, petrov_user_point])
    fake_uow = FakeUsersUnitOfWork(
        fake_user_repo=user_repo, fake_users_statistics=user_point_repo
    )
    return UserService(uow=fake_uow)


@pytest.fixture()
def new_user_dto():
    return UserCreateDTO(
        email='oleg@mail.com',
        first_name='Oleg',
        last_name='Olegov',
        telephone='+79003333333',
        password='Oleg!111',
    )
