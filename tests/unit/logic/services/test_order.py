import pytest


class TestOrderService:
    async def test_add_schedule_correct(self, order_service_with_data, new_order_dto, user_ivanov, new_order_model):
        new_order = await order_service_with_data.add_order(new_order_dto, user_ivanov)

        assert new_order == new_order_model
        assert new_order_model in order_service_with_data.uow.orders.models
        assert order_service_with_data.uow.committed
