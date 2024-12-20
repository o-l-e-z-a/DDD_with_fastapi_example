import pytest

from src.domain.schedules.exceptions import SlotOccupiedException
from src.logic.exceptions.order_exceptions import NotUserOrderLogicException


class TestOrderService:
    async def test_add_order_compare_order_model(
        self, order_service_with_data, new_order_dto, user_ivanov, new_order_model
    ):
        new_order = await order_service_with_data.add_order(new_order_dto, user_ivanov)

        assert new_order == new_order_model
        assert new_order_model in order_service_with_data.uow.orders.models
        assert order_service_with_data.uow.committed

    async def test_add_order_check_inventory_stock_count(
        self, order_service_with_data, new_order_dto, user_ivanov, stock_count_after_order
    ):
        new_order = await order_service_with_data.add_order(new_order_dto, user_ivanov)

        for i, consumable in enumerate(sorted(new_order.slot.schedule.service.consumables, key=lambda el: el.id)):
            assert consumable.inventory.stock_count.as_generic_type() == stock_count_after_order[i]

    async def test_add_order_check_user_point(
        self, order_service_with_data, new_order_dto, user_ivanov, user_point_ivanov_after_order
    ):
        await order_service_with_data.add_order(new_order_dto, user_ivanov)

        new_user_point = await order_service_with_data.uow.user_points.find_one_or_none(user_id=user_ivanov.id)
        assert new_user_point.count.as_generic_type() == user_point_ivanov_after_order
        assert order_service_with_data.uow.committed

    async def test_add_order_slot_occupied_exception(
        self, order_service_with_data, new_order_dto, user_ivanov, new_order_model
    ):
        new_order_dto.time_start = "12:00"

        with pytest.raises(SlotOccupiedException):
            await order_service_with_data.add_order(new_order_dto, user_ivanov)

        assert not order_service_with_data.uow.committed

    async def test_update_order_compare_order_model(
        self, order_service_with_data, order_update_dto, user_ivanov
    ):
        new_order = await order_service_with_data.update_order(order_update_dto, user_ivanov)

        assert new_order.slot.time_start.as_generic_type() == order_update_dto.time_start
        assert order_service_with_data.uow.committed

    async def test_update_order_not_user_order_exception(
        self, order_service_with_data, order_update_dto, user_petrov
    ):
        with pytest.raises(NotUserOrderLogicException):
            await order_service_with_data.update_order(order_update_dto, user_petrov)

        assert not order_service_with_data.uow.committed

    async def test_delete_order_check_inventory_stock_count(
        self, order_service_with_data, henna_staining_today_14_order, user_ivanov, stock_count_after_delete_order
    ):
        await order_service_with_data.delete_order(henna_staining_today_14_order.id, user_ivanov)

        for i, consumable in enumerate(
            sorted(henna_staining_today_14_order.slot.schedule.service.consumables, key=lambda el: el.id)
        ):
            assert consumable.inventory.stock_count.as_generic_type() == stock_count_after_delete_order[i]
