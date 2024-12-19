import pytest

from src.logic.exceptions.order_exceptions import NotUserOrderLogicException


class TestOrderService:
    async def test_add_order_correct_compare_model(
        self, order_service_db_data, new_order_dto, new_order_model, user_ivanov
    ):
        new_order = await order_service_db_data.add_order(new_order_dto, user_ivanov)

        assert new_order.id
        assert new_order == new_order_model
