import pytest

from src.domain.base.values import CountNumber, PositiveIntNumber
from src.domain.orders.entities import TotalAmountResult, TotalAmountDomainService
from src.domain.orders.events import OrderCreatedEvent
from src.domain.orders.values import LESS_POINT_WARNINGS, MINIMUM_BALANCE, MORE_POINT_WARNINGS
from src.domain.schedules.entities import SlotsForSchedule, Order, OrderStatus
from src.domain.schedules.exceptions import SlotOccupiedException, SlotServiceInvalidException
from src.domain.schedules.values import SlotTime


class TestTotalAmount:
    def test_total_amount_with_all_values(self, ivanov_user_point, promotion_20, henna_staining_service):
        input_user_point = CountNumber(150)
        total_amount = TotalAmountDomainService().calculate(
            promotion=promotion_20, user_point=ivanov_user_point,
            service=henna_staining_service, input_user_point=input_user_point
        )
        expected_total_amount = int(1500 * 0.8 - 150)
        expected_total_amount_result = TotalAmountResult(
            point_uses=input_user_point.as_generic_type(), promotion_sale=int(1500 * 0.2),
            warnings=[], total_amount=expected_total_amount
        )

        total_amount_result = total_amount

        assert expected_total_amount_result == total_amount_result

    def test_total_amount_without_promotion(self, ivanov_user_point, promotion_20, henna_staining_service):
        input_user_point = CountNumber(150)
        total_amount = TotalAmountDomainService().calculate(
            promotion=None, user_point=ivanov_user_point,
            service=henna_staining_service, input_user_point=input_user_point
        )
        expected_total_amount = 1500 - 150
        expected_total_amount_result = TotalAmountResult(
            point_uses=input_user_point.as_generic_type(), promotion_sale=0,
            warnings=[], total_amount=expected_total_amount
        )

        total_amount_result = total_amount

        assert expected_total_amount_result == total_amount_result

    def test_total_amount_more_point_warning(self, ivanov_user_point, promotion_20, henna_staining_service):
        input_user_point = CountNumber(700)
        henna_staining_service.price = PositiveIntNumber(680)
        total_amount = TotalAmountDomainService().calculate(
            promotion=promotion_20, user_point=ivanov_user_point,
            service=henna_staining_service, input_user_point=input_user_point
        )
        expected_total_amount = MINIMUM_BALANCE
        expected_total_amount_result = TotalAmountResult(
            point_uses=344, promotion_sale=int(680 * 0.2),
            warnings=[MORE_POINT_WARNINGS], total_amount=expected_total_amount
        )

        total_amount_result = total_amount

        assert expected_total_amount_result == total_amount_result

    def test_total_amount_less_point_warning(self, ivanov_user_point, promotion_20, henna_staining_service):
        input_user_point = CountNumber(700)
        ivanov_user_point.count = CountNumber(1)
        total_amount = TotalAmountDomainService().calculate(
            promotion=promotion_20, user_point=ivanov_user_point,
            service=henna_staining_service, input_user_point=input_user_point
        )
        expected_total_amount = int(1500 * 0.8)
        expected_total_amount_result = TotalAmountResult(
            point_uses=0, promotion_sale=int(1500 * 0.2),
            warnings=[LESS_POINT_WARNINGS], total_amount=expected_total_amount
        )

        total_amount_result = total_amount

        assert expected_total_amount_result == total_amount_result


# class TestSlotsForSchedule:
#     def test_get_free_slots(
#         self, henna_staining_today_12_slot, henna_staining_today_14_slot, slot_time_for_henna_staining_today_schedule
#     ):
#         s = SlotsForSchedule()
#
#         actual_free_slots = s.get_free_slots([henna_staining_today_12_slot, henna_staining_today_14_slot])
#
#         assert slot_time_for_henna_staining_today_schedule == actual_free_slots
#
#     def test_check_slot_time_is_free(self, henna_staining_today_12_slot, henna_staining_today_14_slot):
#         s = SlotsForSchedule()
#         slot_time = SlotTime('15:00')
#
#         actual_time_is_free = s.check_slot_time_is_free(
#             slot_time, [henna_staining_today_12_slot, henna_staining_today_14_slot]
#         )
#
#         assert actual_time_is_free
#
#     def test_check_slot_time_is_not_free(self, henna_staining_today_12_slot, henna_staining_today_14_slot):
#         s = SlotsForSchedule()
#         slot_time = henna_staining_today_14_slot.time_start
#
#         actual_time_is_free = s.check_slot_time_is_free(
#             slot_time, [henna_staining_today_12_slot, henna_staining_today_14_slot]
#         )
#
#         assert not actual_time_is_free


class TestOrder:
    def test_add_valid(
        self, henna_staining_today_12_slot, henna_staining_today_14_slot, henna_staining_today_15_slot,
        user_ivanov, promotion_20, henna_staining_service, shampooing_service
    ):
        new_order = Order.add(
            # promotion=promotion_20,
            # input_user_point=input_user_point,
            # user_point=ivanov_user_point,
            user_id=user_ivanov.id,
            service_id=henna_staining_service.id,
            slot_id=henna_staining_today_15_slot.id,
            occupied_slots=[henna_staining_today_12_slot, henna_staining_today_14_slot],
            schedule_master_services=[henna_staining_service, shampooing_service]
        )

        assert new_order.user_id == user_ivanov.id
        assert new_order.service_id == henna_staining_service.id
        assert new_order.slot_id == henna_staining_today_15_slot.id
        assert new_order.status == OrderStatus.RECEIVED

    def test_add_valid_event(
        self, henna_staining_today_12_slot, henna_staining_today_14_slot, henna_staining_today_15_slot,
        user_ivanov, promotion_20, henna_staining_service, shampooing_service
    ):
        new_order = Order.add(
            # promotion=promotion_20,
            # input_user_point=input_user_point,
            # user_point=ivanov_user_point,
            user_id=user_ivanov.id,
            service_id=henna_staining_service.id,
            slot_id=henna_staining_today_15_slot.id,
            occupied_slots=[henna_staining_today_12_slot, henna_staining_today_14_slot],
            schedule_master_services=[henna_staining_service, shampooing_service]
        )
        [new_order_event] = new_order.pull_events()

        assert isinstance(new_order_event, OrderCreatedEvent)
        assert new_order_event.user_id == user_ivanov.id
        assert new_order_event.service_id == henna_staining_service.id
        assert new_order_event.slot_id == henna_staining_today_15_slot.id

    def test_add_slot_time_occupied(
        self, henna_staining_today_12_slot, henna_staining_today_14_slot,
        user_ivanov, promotion_20, henna_staining_service, shampooing_service
    ):
        with pytest.raises(SlotOccupiedException):
            Order.add(
                # promotion=promotion_20,
                # input_user_point=input_user_point,
                user_id=user_ivanov.id,
                service_id=henna_staining_service.id,
                slot_id=henna_staining_today_12_slot.id,
                occupied_slots=[henna_staining_today_12_slot, henna_staining_today_14_slot],
                schedule_master_services=[henna_staining_service, shampooing_service]
            )

    def test_add_slot_service_invalid(
        self, henna_staining_today_12_slot, henna_staining_today_14_slot, henna_staining_today_15_slot,
        user_ivanov, promotion_20, henna_staining_service, shampooing_service
    ):
        with pytest.raises(SlotServiceInvalidException):
            Order.add(
                # promotion=promotion_20,
                # input_user_point=input_user_point,
                user_id=user_ivanov.id,
                service_id=henna_staining_service.id,
                slot_id=henna_staining_today_15_slot.id,
                occupied_slots=[henna_staining_today_12_slot, henna_staining_today_14_slot],
                schedule_master_services=[shampooing_service]
            )
