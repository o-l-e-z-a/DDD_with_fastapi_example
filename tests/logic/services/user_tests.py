import pytest

from src.presentation.api.exceptions import UserAlreadyExistsException


class TestUserService:
    async def test_add_user_correct(self, user_service_with_data, new_user_dto, new_user_model, new_user_point_model):
        await user_service_with_data.add_user(new_user_dto)

        assert new_user_model in user_service_with_data.uow.users.models
        assert new_user_point_model in user_service_with_data.uow.user_points.models
        assert user_service_with_data.uow.committed

    async def test_add_user_already_exists_exception(self, user_service_with_data, user_ivanov_dto):
        with pytest.raises(UserAlreadyExistsException):
            await user_service_with_data.add_user(user_ivanov_dto)

        assert not user_service_with_data.uow.committed

    async def test_get_user_by_id_correct(self, user_service_with_data, user_ivanov):
        user = await user_service_with_data.get_user_by_id(user_ivanov.id)

        assert user == user_ivanov

    async def test_get_user_by_id_none(self, user_service_with_data, new_user_model):
        user = await user_service_with_data.get_user_by_id(new_user_model.id)

        assert not user

    async def test_get_user_point_correct(self, user_service_with_data, user_ivanov, ivanov_user_point):
        user_point = await user_service_with_data.get_user_point(user_ivanov)

        assert user_point == ivanov_user_point

    async def test_get_user_point_none(self, user_service_with_data, new_user_model, new_user_point_model):
        user_point = await user_service_with_data.get_user_point(new_user_model)

        assert not user_point
