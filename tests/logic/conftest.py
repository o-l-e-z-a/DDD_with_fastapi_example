import pytest

from src.logic.dto.user_dto import UserCreateDTO
from src.logic.services.users_service import UserService, get_password_hash
from tests.domain.conftest import *

from .mocs import FakeUserPointRepository, FakeUserRepository, FakeUsersUnitOfWork


@pytest.fixture()
def fake_user_repo_with_data(user_ivanov, user_petrov):
    user_repo = FakeUserRepository(models=[user_ivanov, user_petrov])
    return user_repo


@pytest.fixture()
def fake_user_point_repo_with_data(ivanov_user_point, petrov_user_point):
    user_point_repo = FakeUserPointRepository(models=[ivanov_user_point, petrov_user_point])
    return user_point_repo


@pytest.fixture()
def user_service_with_data(fake_user_repo_with_data, fake_user_point_repo_with_data):
    fake_uow = FakeUsersUnitOfWork(
        fake_user_repo=fake_user_repo_with_data,
        fake_users_statistics=fake_user_point_repo_with_data
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


@pytest.fixture()
def user_ivanov_dto(user_ivanov):
    return UserCreateDTO(
        email=user_ivanov.email.as_generic_type(),
        first_name=user_ivanov.first_name.as_generic_type(),
        last_name=user_ivanov.last_name.as_generic_type(),
        telephone=user_ivanov.telephone.as_generic_type(),
        password='Oleg!111',
    )


@pytest.fixture()
def new_user_model(new_user_dto):
    u = User(
        email=Email(new_user_dto.email), first_name=HumanName(new_user_dto.first_name),
        last_name=HumanName(new_user_dto.last_name), telephone=Telephone(new_user_dto.telephone),
    )
    u.id = 3
    return u


@pytest.fixture()
def new_user_point_model(new_user_model):
    return UserPoint(user=new_user_model)


@pytest.fixture()
def fake_user_repo_with_new_user(fake_user_repo_with_data, new_user_model):
    fake_user_repo_with_data.models.append(new_user_model)
    return fake_user_repo_with_data
