import pytest

from src.logic.exceptions.user_exceptions import UserAlreadyExistsLogicException, UserPointNotFoundLogicException


class TestUserService:
    async def test_add_user_correct_compare_model(self, user_service_db_data, new_user_dto, new_user_model):
        new_user = await user_service_db_data.add_user(new_user_dto)

        assert new_user.id
        assert new_user == new_user_model

    async def test_add_user_exist_in_all_query(self, user_service_db_data, new_user_dto, new_user_model, user_repo):
        await user_service_db_data.add_user(new_user_dto)

        all_users = await user_repo.find_all()
        assert len(all_users) == 3
        assert new_user_model in all_users

    async def test_add_user_already_exists_exception(self, user_service_db_data, user_ivanov_dto):
        with pytest.raises(UserAlreadyExistsLogicException):
            await user_service_db_data.add_user(user_ivanov_dto)

    async def test_get_user_point_correct(self, user_service_db_data, user_ivanov, ivanov_user_point):
        user_point = await user_service_db_data.get_user_point(user_ivanov)

        assert user_point == ivanov_user_point

    async def test_get_user_point_correct_not_exists_exception(self, user_service_db_data, new_user_model):
        with pytest.raises(UserPointNotFoundLogicException):
            await user_service_db_data.get_user_point(new_user_model)
