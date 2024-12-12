from datetime import date, timedelta

import pytest

from src.domain.base.values import CountNumber, Name, PositiveIntNumber
from src.domain.orders.entities import Order, Promotion
from src.domain.schedules.entities import Consumable, Inventory, Master, Schedule, Service, Slot
from src.domain.schedules.values import SlotTime
from src.domain.users.entities import User, UserPoint
from src.domain.users.values import Email, HumanName, Telephone

TODAY = date(year=2024, month=7, day=8)
TOMORROW = date(year=2024, month=7, day=9)


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
    user_point = UserPoint(user=user_ivanov, count=CountNumber(700))
    user_point.id = 1
    return user_point


@pytest.fixture()
def petrov_user_point(user_petrov):
    user_point = UserPoint(user=user_petrov, count=CountNumber(0))
    user_point.id = 2
    return user_point


@pytest.fixture()
def henna_inventory():
    inventory = Inventory(name=Name('henna'), unit=Name('ml'), stock_count=CountNumber(1000))
    inventory.id = 1
    return inventory


@pytest.fixture()
def henna_consumable(henna_inventory):
    consumable = Consumable(inventory=henna_inventory, count=PositiveIntNumber(5))
    consumable.id = 1
    return consumable


@pytest.fixture()
def shampoo_inventory():
    inventory = Inventory(name=Name('shampoo'), unit=Name('ml'), stock_count=CountNumber(1000))
    inventory.id = 2
    return inventory


@pytest.fixture()
def shampoo_consumable(shampoo_inventory):
    consumable = Consumable(inventory=shampoo_inventory, count=PositiveIntNumber(10))
    consumable.id = 2
    return consumable


@pytest.fixture()
def henna_staining_service(henna_consumable, shampoo_consumable):
    service = Service(
        consumables=[henna_consumable, shampoo_consumable], name=Name('henna staining'),
        description='includes shampooing and henna staining', price=PositiveIntNumber(1500)
    )
    service.id = 1
    return service


@pytest.fixture()
def shampooing_service(shampoo_consumable):
    service = Service(
        consumables=[shampoo_consumable], name=Name('shampooing'),
        description='includes shampooing', price=PositiveIntNumber(500)
    )
    service.id = 2
    return service


@pytest.fixture()
def henna_master(user_petrov, henna_staining_service):
    master = Master(
        user=user_petrov, services=[henna_staining_service, shampooing_service], description='master of henna staining'
    )
    master.id = 1
    return master


@pytest.fixture()
def henna_staining_today_schedule(henna_staining_service, henna_master):
    schedule = Schedule(
        service=henna_staining_service, master=henna_master, day=TODAY
    )
    schedule.id = 1
    return schedule


@pytest.fixture()
def shampooing_tomorrow_schedule(shampooing_service, henna_master):
    schedule = Schedule(
        service=shampooing_service, master=henna_master, day=TOMORROW
    )
    schedule.id = 2
    return schedule


@pytest.fixture()
def henna_staining_today_12_slot(henna_staining_today_schedule):
    slot = Slot(schedule=henna_staining_today_schedule, time_start=SlotTime("12:00"))
    slot.id = 1
    return slot


@pytest.fixture()
def henna_staining_today_14_slot(henna_staining_today_schedule):
    slot = Slot(schedule=henna_staining_today_schedule, time_start=SlotTime("14:00"))
    slot.id = 2
    return slot


@pytest.fixture()
def henna_staining_today_15_slot(henna_staining_today_schedule):
    slot = Slot(schedule=henna_staining_today_schedule, time_start=SlotTime("15:00"))
    slot.id = 3
    return slot


@pytest.fixture()
def henna_staining_today_14_order(henna_staining_today_14_slot, user_ivanov):
    order = Order(
        user=user_ivanov,
        slot=henna_staining_today_14_slot,
        point_uses=CountNumber(100),
        promotion_sale=CountNumber(0),
        total_amount=PositiveIntNumber(1400),
    )
    order.id = 1
    return order


@pytest.fixture()
def henna_staining_today_12_order(henna_staining_today_12_slot, user_petrov):
    order = Order(
        user=user_petrov,
        slot=henna_staining_today_12_slot,
        point_uses=CountNumber(0),
        promotion_sale=CountNumber(0),
        total_amount=PositiveIntNumber(500),
    )
    order.id = 2
    return order
