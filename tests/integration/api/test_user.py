import pytest

from httpx import AsyncClient

from src.presentation.api.users.utils import (
    ACCESS_TOKEN_COOKIE_FIELD,
    ACCESS_TOKEN_RESPONSE_FIELD,
    REFRESH_TOKEN_RESPONSE_FIELD,
)


class TestRegisterRouter:
    url = "/auth/register/"

    async def test_register_user_compare_model(
        self, ac: AsyncClient, user_service_with_db_data, new_user_dto, new_user_model
    ):
        response = await ac.post(self.url, json=new_user_dto.model_dump())

        assert response.status_code == 201
        assert response.json() == new_user_model.to_dict()

    async def test_add_user_already_exists_exception(self, ac: AsyncClient, user_service_with_db_data, user_ivanov_dto):
        response = await ac.post(self.url, json=user_ivanov_dto.model_dump())

        assert response.status_code == 409
        assert response.json() == {
            'detail': 'Пользователь c email: ivanov@mail.ru или номером: 880005553535 - существует'
        }


class TestLoginRouter:
    url = "/auth/login/"

    async def test_register_user_compare_model(
        self, ac: AsyncClient, user_service_with_db_data, user_ivanov_dto
    ):
        response = await ac.post(self.url, json=user_ivanov_dto.model_dump())

        assert response.status_code == 200
        assert response.cookies.get(ACCESS_TOKEN_COOKIE_FIELD)
        assert ACCESS_TOKEN_RESPONSE_FIELD in response.json()
        assert REFRESH_TOKEN_RESPONSE_FIELD in response.json()
