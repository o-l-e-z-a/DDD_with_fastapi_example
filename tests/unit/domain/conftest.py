from datetime import date, timedelta

import pytest

from src.domain.base.values import CountNumber, Name, PositiveIntNumber
from src.domain.orders.entities import Promotion, UserPoint
from src.domain.schedules.entities import Master, Schedule, Service, Slot, Order
from src.domain.schedules.values import END_HOUR, START_HOUR, SlotTime
from src.domain.users.entities import User
from src.domain.users.values import Email, HumanName, Telephone

TODAY = date(year=2024, month=7, day=8)
TOMORROW = date(year=2024, month=7, day=9)
PASSWORD = "Admin@66"


@pytest.fixture()
def promotion_20():
    promotion = Promotion(
        code=Name('sale_20'), day_start=TODAY, is_active=True,
        day_end=TODAY + timedelta(days=7), sale=PositiveIntNumber(20)
    )
    return promotion


@pytest.fixture()
def user_ivanov():
    user = User(
        email=Email('ivanov@mail.ru'), first_name=HumanName('Ivan'),
        last_name=HumanName('Ivanov'), telephone=Telephone('880005553535')
    )
    user.id = 1
    return user


@pytest.fixture()
def user_petrov():
    user = User(
        email=Email('petrov@mail.ru'), first_name=HumanName('Petr'),
        last_name=HumanName('Petrov'), telephone=Telephone('880005553636')
    )
    user.id = 2
    return user


@pytest.fixture()
def ivanov_user_point(user_ivanov):
    user_point = UserPoint(user_id=user_ivanov.id, count=CountNumber(700))
    user_point.id = 1
    return user_point


@pytest.fixture()
def petrov_user_point(user_petrov):
    user_point = UserPoint(user_id=user_petrov.id, count=CountNumber(0))
    user_point.id = 2
    return user_point


# @pytest.fixture()
# def henna_inventory():
#     inventory = Inventory(name=Name('henna'), unit=Name('ml'), stock_count=CountNumber(1000))
#     inventory.id = 1
#     return inventory
#
#
# @pytest.fixture()
# def henna_consumable(henna_inventory):
#     consumable = Consumable(inventory=henna_inventory, count=PositiveIntNumber(5))
#     consumable.id = 1
#     return consumable
#
#
# @pytest.fixture()
# def shampoo_inventory():
#     inventory = Inventory(name=Name('shampoo'), unit=Name('ml'), stock_count=CountNumber(1000))
#     inventory.id = 2
#     return inventory
#
#
# @pytest.fixture()
# def shampoo_consumable(shampoo_inventory):
#     consumable = Consumable(inventory=shampoo_inventory, count=PositiveIntNumber(10))
#     consumable.id = 2
#     return consumable


@pytest.fixture()
def henna_staining_service():
    service = Service(
        # consumables=[henna_consumable, shampoo_consumable],
        name=Name('henna staining'),
        description='includes shampooing and henna staining',
        price=PositiveIntNumber(1500)
    )
    service.id = 1
    return service


@pytest.fixture()
def shampooing_service():
    service = Service(
        # consumables=[shampoo_consumable],
        name=Name('shampooing'),
        description='includes shampooing',
        price=PositiveIntNumber(500)
    )
    service.id = 2
    return service


@pytest.fixture()
def henna_and_shampooing_master(user_petrov, henna_staining_service, shampooing_service):
    master = Master(
        user_id=user_petrov.id,
        services_id=[henna_staining_service.id, shampooing_service.id],
        description='master of henna staining'
    )
    master.id = 1
    return master


@pytest.fixture()
def henna_staining_today_schedule(henna_and_shampooing_master):
    schedule = Schedule.add(
        master_id=henna_and_shampooing_master.id,
        day=TODAY
    )
    set_slots_id(schedule, start_id=1)
    schedule.id = 1
    return schedule


def set_slots_id(schedule, start_id):
    for slot in schedule.slots:
        slot.id = start_id
        start_id += 1


@pytest.fixture()
def shampooing_tomorrow_schedule(shampooing_service, henna_and_shampooing_master):
    schedule = Schedule(
        master_id=henna_and_shampooing_master.id,
        day=TOMORROW
    )
    set_slots_id(schedule, start_id=11)
    schedule.id = 2
    return schedule


@pytest.fixture()
def henna_staining_today_12_slot(henna_staining_today_schedule):
    for slot in henna_staining_today_schedule.slots:
        if slot.time_start == SlotTime("12:00"):
            return slot


@pytest.fixture()
def henna_staining_today_14_slot(henna_staining_today_schedule):
    for slot in henna_staining_today_schedule.slots:
        if slot.time_start == SlotTime("14:00"):
            return slot


@pytest.fixture()
def slot_time_for_henna_staining_today_schedule():
    slot_time = \
        [SlotTime(f'{t}:00') for t in range(START_HOUR, 12)] \
        + [SlotTime('13:00')] \
        + [SlotTime(f'{t}:00') for t in range(15, END_HOUR + 1)]
    return slot_time


@pytest.fixture()
def henna_staining_today_15_slot(henna_staining_today_schedule):
    for slot in henna_staining_today_schedule.slots:
        if slot.time_start == SlotTime("15:00"):
            return slot


@pytest.fixture()
def henna_staining_today_14_order(henna_staining_today_14_slot, henna_staining_service, user_ivanov, shampooing_service):
    order = Order.add(
        user_id=user_ivanov,
        service_id=henna_staining_service.id,
        slot_id=henna_staining_today_14_slot.id,
        occupied_slots=[],
        schedule_master_services=[henna_staining_service, shampooing_service]
        # point_uses=CountNumber(100),
        # promotion_sale=CountNumber(0),
        # total_amount=PositiveIntNumber(1400),
    )
    order.id = 1
    return order


@pytest.fixture()
def henna_staining_today_12_order(henna_staining_today_12_slot, henna_staining_service, user_petrov, shampooing_service):
    order = Order.add(
        user_id=user_petrov,
        service_id=henna_staining_service.id,
        slot_id=henna_staining_today_12_slot,
        occupied_slots=[],
        schedule_master_services=[henna_staining_service, shampooing_service]
        # point_uses=CountNumber(0),
        # promotion_sale=CountNumber(0),
        # total_amount=PositiveIntNumber(500),
    )
    order.id = 2
    return order
