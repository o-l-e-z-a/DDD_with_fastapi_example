import pytest

from src.domain.schedules.exceptions import SlotOccupiedException
from src.logic.exceptions.order_exceptions import NotUserOrderLogicException


class TestOrderService:
    async def test_add_order_correct_compare_model(
        self, order_service_db_data, new_order_dto, new_order_model, user_ivanov
    ):
        new_order = await order_service_db_data.add_order(new_order_dto, user_ivanov)

        assert new_order.id
        assert new_order == new_order_model

    async def test_add_order_check_inventory_stock_count(
        self,
        order_service_db_data,
        service_repo,
        new_order_dto,
        user_ivanov,
        henna_staining_today_schedule,
        stock_count_after_order
    ):
        await order_service_db_data.add_order(new_order_dto, user_ivanov)

        service = await service_repo.get_service_with_consumable(henna_staining_today_schedule.service.id)
        for i, consumable in enumerate(sorted(service.consumables, key=lambda el: el.id)):
            assert consumable.inventory.stock_count.as_generic_type() == stock_count_after_order[i]

    async def test_add_order_check_user_point(
        self,
        order_service_db_data,
        user_point_repo,
        new_order_dto,
        user_ivanov,
        user_point_ivanov_after_order
    ):
        await order_service_db_data.add_order(new_order_dto, user_ivanov)

        current_user_ivanov_point = await user_point_repo.find_one_or_none(user_id=user_ivanov.id)
        assert current_user_ivanov_point.count.as_generic_type() == user_point_ivanov_after_order

    async def test_add_order_slot_occupied_exception(
        self, order_service_db_data, new_order_dto, user_ivanov
    ):
        new_order_dto.time_start = "12:00"
        with pytest.raises(SlotOccupiedException):
            await order_service_db_data.add_order(new_order_dto, user_ivanov)

    async def test_update_order_compare_order_model(
        self, order_service_db_data, order_update_dto, user_ivanov
    ):
        new_order = await order_service_db_data.update_order(order_update_dto, user_ivanov)

        assert new_order.slot.time_start.as_generic_type() == order_update_dto.time_start

    async def test_update_order_not_user_order_exception(
        self, order_service_db_data, order_update_dto, user_petrov
    ):
        with pytest.raises(NotUserOrderLogicException):
            await order_service_db_data.update_order(order_update_dto, user_petrov)

    async def test_delete_order_check_inventory_stock_count(
        self,
        order_service_db_data,
        service_repo,
        user_ivanov,
        henna_staining_today_14_order,
        stock_count_after_delete_order
    ):
        await order_service_db_data.delete_order(henna_staining_today_14_order.id, user_ivanov)

        service = await service_repo.get_service_with_consumable(henna_staining_today_14_order.slot.schedule.service.id)
        for i, consumable in enumerate(sorted(service.consumables, key=lambda el: el.id)):
            assert consumable.inventory.stock_count.as_generic_type() == stock_count_after_delete_order[i]
