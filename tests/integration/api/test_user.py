import pytest

from httpx import AsyncClient

from src.presentation.api.exceptions import EXCEPTION_DETAIL_FIELD
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
            EXCEPTION_DETAIL_FIELD: 'Пользователь c email: ivanov@mail.ru или номером: 880005553535 - существует'
        }


class TestLoginRouter:
    url = "/auth/login/"

    async def test_login_user_response(
        self, ac: AsyncClient, user_service_with_db_data, user_ivanov_dto
    ):
        response = await ac.post(self.url, json=user_ivanov_dto.model_dump())

        assert response.status_code == 200
        assert response.cookies.get(ACCESS_TOKEN_COOKIE_FIELD)

    async def test_login_user_cookie(
        self, ac: AsyncClient, user_service_with_db_data, user_ivanov_dto
    ):
        response = await ac.post(self.url, json=user_ivanov_dto.model_dump())

        assert ACCESS_TOKEN_RESPONSE_FIELD in response.json()
        assert REFRESH_TOKEN_RESPONSE_FIELD in response.json()

    async def test_login_invalid_user(
        self, ac: AsyncClient, user_service_with_db_data, new_user_dto
    ):
        response = await ac.post(self.url, json=new_user_dto.model_dump())

        assert response.status_code == 401
        assert response.json() == {EXCEPTION_DETAIL_FIELD: 'Неверная почта или пароль'}


class TestMeRouter:
    url = "/users/me/"

    async def test_user_me_compare_model(
        self, ac_with_login_ivanov: AsyncClient, user_ivanov
    ):
        response = await ac_with_login_ivanov.get(self.url)

        assert response.status_code == 200
        assert response.json() == user_ivanov.to_dict()

    async def test_user_me_token_absent(
        self, ac: AsyncClient
    ):
        response = await ac.get(self.url)

        assert response.status_code == 401
        assert response.json() == {EXCEPTION_DETAIL_FIELD: 'Токен отсутствует'}

    async def test_user_me_expired_signature_error(
        self, ac: AsyncClient, old_access_token
    ):
        response = await ac.get(self.url, cookies={ACCESS_TOKEN_COOKIE_FIELD: old_access_token})

        assert response.status_code == 401
        assert response.json() == {EXCEPTION_DETAIL_FIELD: 'Срок действия токена истек'}

    async def test_user_me_invalid_format_error(
        self, ac: AsyncClient, invalid_access_token
    ):
        response = await ac.get(self.url, cookies={ACCESS_TOKEN_COOKIE_FIELD: invalid_access_token})

        assert response.status_code == 401
        assert response.json() == {EXCEPTION_DETAIL_FIELD: 'Неверный формат токена'}


class TestUserPointRouter:
    url = "/users/user_point/"

    async def test_user_point_compare_model(
        self, ac_with_login_ivanov: AsyncClient, ivanov_user_point
    ):
        response = await ac_with_login_ivanov.get(self.url)

        assert response.status_code == 200
        assert response.json() == {'count': ivanov_user_point.count.as_generic_type()}

    async def test_user_point_user_point_not_found(
        self, ac: AsyncClient, user_ivanov_db, user_ivanov_dto
    ):
        await ac.post("/auth/login/", json=user_ivanov_dto.model_dump())

        response = await ac.get(self.url)

        assert response.status_code == 404
        assert response.json() == {EXCEPTION_DETAIL_FIELD: f"Баллы пользователя с id {user_ivanov_db.id} не был найден"}
