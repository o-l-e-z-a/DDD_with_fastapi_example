import pytest

from src.logic.exceptions.schedule_exceptions import MasterNotFoundLogicException, ServiceNotFoundLogicException


def remove_consumables_from_schedule_service(schedule):
    schedule.service.consumables = []
    for service in schedule.master.services:
        service.consumables = []


class TestScheduleService:
    async def test_add_schedule_correct_compare_model(
        self, schedule_service_db_data, new_schedule_dto, new_schedule_model
    ):
        remove_consumables_from_schedule_service(new_schedule_model)

        new_schedule = await schedule_service_db_data.add_schedule(new_schedule_dto)

        assert new_schedule.id
        assert new_schedule == new_schedule_model

    async def test_add_schedule_exist_in_all_query(
        self, schedule_service_db_data, new_schedule_dto, new_schedule_model, schedule_repo
    ):
        remove_consumables_from_schedule_service(new_schedule_model)

        await schedule_service_db_data.add_schedule(new_schedule_dto)

        all_schedules = await schedule_repo.find_all()
        assert len(all_schedules) == 3
        assert new_schedule_model in all_schedules

    async def test_day_for_master(self, schedule_service_db_data, henna_and_shampooing_master_db, henna_master_days):
        days = await schedule_service_db_data.get_master_days(master_id=henna_and_shampooing_master_db.id)

        assert days == henna_master_days

    async def test_add_schedule_master_not_found_exception(self, schedule_service_db_data, new_schedule_dto):
        new_schedule_dto.master_id = 999
        with pytest.raises(MasterNotFoundLogicException):
            await schedule_service_db_data.add_schedule(new_schedule_dto)

    async def test_add_schedule_service_not_found_exception(self, schedule_service_db_data, new_schedule_dto):
        new_schedule_dto.service_id = 999
        with pytest.raises(ServiceNotFoundLogicException):
            await schedule_service_db_data.add_schedule(new_schedule_dto)
