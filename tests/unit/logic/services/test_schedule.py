import pytest

from src.logic.exceptions.schedule_exceptions import MasterNotFoundLogicException, ServiceNotFoundLogicException


class TestScheduleService:
    async def test_add_schedule_correct(self, schedule_service_with_data, new_schedule_dto, new_schedule_model):
        new_schedule = await schedule_service_with_data.add_schedule(new_schedule_dto)

        assert new_schedule == new_schedule_model
        assert new_schedule_model in schedule_service_with_data.uow.schedules.models
        assert schedule_service_with_data.uow.committed

    async def test_add_schedule_service_not_found_exception(self, schedule_service_with_data, new_schedule_dto):
        new_schedule_dto.service_id = 999
        with pytest.raises(ServiceNotFoundLogicException):
            await schedule_service_with_data.add_schedule(new_schedule_dto)

        assert not schedule_service_with_data.uow.committed

    async def test_add_schedule_master_not_found_exception(self, schedule_service_with_data, new_schedule_dto):
        new_schedule_dto.master_id = 999
        with pytest.raises(MasterNotFoundLogicException):
            await schedule_service_with_data.add_schedule(new_schedule_dto)

        assert not schedule_service_with_data.uow.committed

    async def test_get_master_days(self, schedule_service_with_data, henna_master, henna_master_days):
        days = await schedule_service_with_data.get_master_days(master_id=henna_master.id)

        assert days == henna_master_days
