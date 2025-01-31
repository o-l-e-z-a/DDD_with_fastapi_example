import pytest

from src.domain.base.values import CountNumber, PositiveIntNumber
from src.domain.orders.entities import Order, TotalAmount, TotalAmountResult
from src.domain.orders.values import LESS_POINT_WARNINGS, MINIMUM_BALANCE, MORE_POINT_WARNINGS
from src.domain.schedules.entities import SlotsForSchedule
from src.domain.schedules.exceptions import SlotOccupiedException
from src.domain.schedules.values import SlotTime


class TestTotalAmount:
    def test_total_amount_with_all_values(self, ivanov_user_point, promotion_20, henna_staining_today_schedule):
        input_user_point = CountNumber(150)
        total_amount = TotalAmount(
            promotion=promotion_20, user_point=ivanov_user_point,
            schedule=henna_staining_today_schedule, input_user_point=input_user_point
        )
        expected_total_amount = int(1500 * 0.8 - 150)
        expected_total_amount_result = TotalAmountResult(
            point_uses=input_user_point.as_generic_type(), promotion_sale=int(1500 * 0.2),
            warnings=[], total_amount=expected_total_amount
        )

        total_amount_result = total_amount.calculate()

        assert expected_total_amount_result == total_amount_result

    def test_total_amount_without_promotion(self, ivanov_user_point, promotion_20, henna_staining_today_schedule):
        input_user_point = CountNumber(150)
        total_amount = TotalAmount(
            promotion=None, user_point=ivanov_user_point,
            schedule=henna_staining_today_schedule, input_user_point=input_user_point
        )
        expected_total_amount = 1500 - 150
        expected_total_amount_result = TotalAmountResult(
            point_uses=input_user_point.as_generic_type(), promotion_sale=0,
            warnings=[], total_amount=expected_total_amount
        )

        total_amount_result = total_amount.calculate()

        assert expected_total_amount_result == total_amount_result

    def test_total_amount_more_point_warning(self, ivanov_user_point, promotion_20, henna_staining_today_schedule):
        input_user_point = CountNumber(700)
        henna_staining_today_schedule.service.price = PositiveIntNumber(680)
        total_amount = TotalAmount(
            promotion=promotion_20, user_point=ivanov_user_point,
            schedule=henna_staining_today_schedule, input_user_point=input_user_point
        )
        expected_total_amount = MINIMUM_BALANCE
        expected_total_amount_result = TotalAmountResult(
            point_uses=344, promotion_sale=int(680 * 0.2),
            warnings=[MORE_POINT_WARNINGS], total_amount=expected_total_amount
        )

        total_amount_result = total_amount.calculate()

        assert expected_total_amount_result == total_amount_result

    def test_total_amount_less_point_warning(self, ivanov_user_point, promotion_20, henna_staining_today_schedule):
        input_user_point = CountNumber(700)
        ivanov_user_point.count = CountNumber(1)
        total_amount = TotalAmount(
            promotion=promotion_20, user_point=ivanov_user_point,
            schedule=henna_staining_today_schedule, input_user_point=input_user_point
        )
        expected_total_amount = int(1500 * 0.8)
        expected_total_amount_result = TotalAmountResult(
            point_uses=0, promotion_sale=int(1500 * 0.2),
            warnings=[LESS_POINT_WARNINGS], total_amount=expected_total_amount
        )

        total_amount_result = total_amount.calculate()

        assert expected_total_amount_result == total_amount_result


class TestSlotsForSchedule:
    def test_get_free_slots(
        self, henna_staining_today_12_slot, henna_staining_today_14_slot, slot_time_for_henna_staining_today_schedule
    ):
        s = SlotsForSchedule()

        actual_free_slots = s.get_free_slots([henna_staining_today_12_slot, henna_staining_today_14_slot])

        assert slot_time_for_henna_staining_today_schedule == actual_free_slots

    def test_check_slot_time_is_free(self, henna_staining_today_12_slot, henna_staining_today_14_slot):
        s = SlotsForSchedule()
        slot_time = SlotTime('15:00')

        actual_time_is_free = s.check_slot_time_is_free(
            slot_time, [henna_staining_today_12_slot, henna_staining_today_14_slot]
        )

        assert actual_time_is_free

    def test_check_slot_time_is_not_free(self, henna_staining_today_12_slot, henna_staining_today_14_slot):
        s = SlotsForSchedule()
        slot_time = henna_staining_today_14_slot.time_start

        actual_time_is_free = s.check_slot_time_is_free(
            slot_time, [henna_staining_today_12_slot, henna_staining_today_14_slot]
        )

        assert not actual_time_is_free


class TestOrderProcess:
    def test_add_valid(
            self, henna_staining_today_12_slot, henna_staining_today_14_slot,
            ivanov_user_point, promotion_20, henna_staining_today_schedule
    ):
        input_user_point = CountNumber(150)
        slot_time = SlotTime('15:00')
        expected_total_amount = int(1500 * 0.8 - 150)
        expected_promotion_sale = int(1500 * 0.2)

        new_order = Order.add(
            promotion=promotion_20, input_user_point=input_user_point, user_point=ivanov_user_point,
            user=ivanov_user_point.user, schedule=henna_staining_today_schedule,
            time_start=slot_time, occupied_slots=[henna_staining_today_12_slot, henna_staining_today_14_slot]
        )

        assert new_order.slot.time_start == slot_time
        assert new_order.point_uses == input_user_point
        assert new_order.promotion_sale == CountNumber(expected_promotion_sale)
        assert new_order.total_amount == PositiveIntNumber(expected_total_amount)
        assert 700 - 150 == ivanov_user_point.count.as_generic_type()
        service = henna_staining_today_schedule.service
        consumable_henna, consumable_shampoo = service.consumables
        assert consumable_henna.inventory.stock_count == CountNumber(995)
        assert consumable_shampoo.inventory.stock_count == CountNumber(990)

    def test_add_slot_time_occupied(
            self, henna_staining_today_12_slot, henna_staining_today_14_slot,
            ivanov_user_point, promotion_20, henna_staining_today_schedule
    ):
        input_user_point = CountNumber(150)
        slot_time = SlotTime('12:00')

        with pytest.raises(SlotOccupiedException):
            Order.add(
                promotion=promotion_20, input_user_point=input_user_point, user_point=ivanov_user_point,
                user=ivanov_user_point.user, schedule=henna_staining_today_schedule,
                time_start=slot_time, occupied_slots=[henna_staining_today_12_slot, henna_staining_today_14_slot]
            )
        assert 700 == ivanov_user_point.count.as_generic_type()
        service = henna_staining_today_schedule.service
        consumable_henna, consumable_shampoo = service.consumables
        assert consumable_henna.inventory.stock_count == CountNumber(1000)
        assert consumable_shampoo.inventory.stock_count == CountNumber(1000)
