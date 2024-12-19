from httpx import AsyncClient

from src.presentation.api.exceptions import EXCEPTION_DETAIL_FIELD


class TestAddScheduleRouter:
    url = "/api/schedule/add/"

    async def test_add_schedule_compare_model(
        self, ac: AsyncClient, schedule_service_db_data, new_schedule_dto, new_schedule_model_added_dict
    ):
        response = await ac.post(self.url, json=new_schedule_dto.model_dump(mode='json'))

        assert response.status_code == 201
        response_json = response.json()
        response_json.pop('id')
        assert response_json == new_schedule_model_added_dict

    async def test_add_schedule_service_not_found_exception(
        self, ac: AsyncClient, schedule_service_db_data, new_schedule_dto, new_schedule_model_added_dict
    ):
        new_schedule_dto.service_id = 999

        response = await ac.post(self.url, json=new_schedule_dto.model_dump(mode='json'))

        assert response.status_code == 404
        assert response.json() == {EXCEPTION_DETAIL_FIELD: 'Сервис с id 999 не был найден'}

    async def test_add_master_service_not_found_exception(
        self, ac: AsyncClient, schedule_service_db_data, new_schedule_dto, new_schedule_model_added_dict
    ):
        new_schedule_dto.master_id = 999

        response = await ac.post(self.url, json=new_schedule_dto.model_dump(mode='json'))

        assert response.status_code == 404
        assert response.json() == {EXCEPTION_DETAIL_FIELD: 'Мастер с id 999 не был найден'}


class TestMasterDaysRouter:
    url = "/api/master_days/"

    async def test_get_master_days(
        self, ac_with_master_login: AsyncClient, henna_master_days
    ):
        response = await ac_with_master_login.get(self.url)

        assert response.status_code == 200
        assert response.json() == {"days": [str(day) for day in henna_master_days]}


class TestDayForMasterRouter:
    url = "/api/master/{master_pk}/service/{service_pk}/schedules/"

    async def test_get_master_days(
        self, ac_with_master_login: AsyncClient, henna_and_shampooing_master, henna_staining_service, henna_master_days
    ):
        url = self.url.format(master_pk=henna_and_shampooing_master.id, service_pk=henna_staining_service.id)

        response = await ac_with_master_login.get(url)

        assert response.status_code == 200
        assert response.json() == {'days': ['2024-07-08']}

    async def test_get_master_days_incorrect_master_pk(
        self, ac_with_master_login: AsyncClient, henna_and_shampooing_master, henna_staining_service, henna_master_days
    ):
        url = self.url.format(master_pk=999, service_pk=henna_staining_service.id)

        response = await ac_with_master_login.get(url)

        assert response.status_code == 200
        assert response.json() == {'days': []}

    async def test_get_master_days_incorrect_service_pk(
        self, ac_with_master_login: AsyncClient, henna_and_shampooing_master, henna_staining_service, henna_master_days
    ):
        url = self.url.format(master_pk=henna_and_shampooing_master.id, service_pk=999)

        response = await ac_with_master_login.get(url)

        assert response.status_code == 200
        assert response.json() == {'days': []}


class TestSlotForDayRouter:
    url = "/api/slots/{schedule_pk}/"

    async def test_get_slot_for_day(
        self,
        ac_with_master_login: AsyncClient,
        henna_staining_today_schedule,
        slot_time_for_henna_staining_today_schedule
    ):
        url = self.url.format(schedule_pk=henna_staining_today_schedule.id)
        expected = {'slots': [slot.as_generic_type() for slot in slot_time_for_henna_staining_today_schedule]}

        response = await ac_with_master_login.get(url)

        assert response.status_code == 200
        assert response.json() == expected

    async def test_get_slot_for_day_incorrect_schedule(
        self,
        ac_with_master_login: AsyncClient,
    ):
        url = self.url.format(schedule_pk=999)

        response = await ac_with_master_login.get(url)

        assert response.status_code == 404
        assert response.json() == {EXCEPTION_DETAIL_FIELD: 'Расписание с id 999 не был найден'}
