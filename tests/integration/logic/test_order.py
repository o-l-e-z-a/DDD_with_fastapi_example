import pytest

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
