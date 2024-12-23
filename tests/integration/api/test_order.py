from httpx import AsyncClient

from src.presentation.api.exceptions import EXCEPTION_DETAIL_FIELD


class TestAddOrderRouter:
    url = "/api/order/add/"

    async def test_add_order(
        self,
        ac_with_login_ivanov: AsyncClient,
        order_service_db_data,
        new_order_add_schema,
        new_order_added_dict
    ):
        response = await ac_with_login_ivanov.post(self.url, json=new_order_add_schema.model_dump(mode='json'))

        assert response.status_code == 201
        response_json = response.json()
        response_json.pop('id')
        response_json.pop('date_add')
        assert response_json == new_order_added_dict

    async def test_add_order_slot_occupied_exception(
        self,
        ac_with_login_ivanov: AsyncClient,
        order_service_db_data,
        new_order_add_schema,
        new_order_added_dict
    ):
        new_order_add_schema.slot.time_start = "12:00"

        response = await ac_with_login_ivanov.post(self.url, json=new_order_add_schema.model_dump(mode='json'))

        assert response.status_code == 400
        assert response.json() == {EXCEPTION_DETAIL_FIELD: 'Времянное окно некорректно или уже занято'}

    async def test_add_order_service_not_found_exception(
        self,
        ac_with_login_ivanov: AsyncClient,
        new_order_add_schema,
        new_order_added_dict
    ):
        new_order_add_schema.slot.schedule_id = 999

        response = await ac_with_login_ivanov.post(self.url, json=new_order_add_schema.model_dump(mode='json'))

        assert response.status_code == 404
        assert response.json() == {EXCEPTION_DETAIL_FIELD: 'Расписание с id 999 не был найден'}


class TestUpdateOrder:
    url = '/api/order/{order_id}/update/'

    async def test_update_order(
        self,
        ac_with_login_ivanov: AsyncClient,
        order_service_db_data,
        order_update_dto,
        new_order_added_dict
    ):
        url = self.url.format(order_id=order_update_dto.order_id)
        response = await ac_with_login_ivanov.put(
            url, json=order_update_dto.model_dump(include='time_start', mode='json')
        )

        assert response.status_code == 200
        response_json = response.json()
        assert response_json['slot']['time_start'] == order_update_dto.time_start

    async def test_update_order_not_found_exception(
        self,
        ac_with_login_ivanov: AsyncClient,
        order_service_db_data,
        order_update_dto,
        new_order_added_dict
    ):
        url = self.url.format(order_id=999)
        response = await ac_with_login_ivanov.put(
            url, json=order_update_dto.model_dump(include='time_start', mode='json')
        )

        assert response.status_code == 404
        assert response.json() == {EXCEPTION_DETAIL_FIELD: 'Заказ с id 999 не был найден'}
