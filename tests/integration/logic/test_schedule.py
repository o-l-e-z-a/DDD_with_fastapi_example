import pytest


class TestScheduleService:
    async def test_add_schedule_correct_compare_model(
        self, schedule_service_db_data, new_schedule_dto, new_schedule_model
    ):
        print("test 1")
        new_schedule_model.service.consumables = []
        for service in new_schedule_model.master.services:
            service.consumables = []

        new_schedule = await schedule_service_db_data.add_schedule(new_schedule_dto)

        assert new_schedule.id
        assert new_schedule == new_schedule_model

    async def test_add_schedule_exist_in_all_query(
        self, schedule_service_db_data, new_schedule_dto, new_schedule_model, schedule_repo
    ):
        print("test 2")
        await schedule_service_db_data.add_schedule(new_schedule_dto)

        all_schedules = await schedule_repo.find_all()
        assert len(all_schedules) == 3
        assert new_schedule_model in all_schedules
