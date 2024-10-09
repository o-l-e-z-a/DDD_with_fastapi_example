from datetime import date, timedelta

import pytest

from src.domain.base.values import CountNumber, Name, PositiveIntNumber
from src.domain.orders.entities import Promotion
from src.domain.schedules.entities import Consumable, Inventory, Master, Schedule, Service, Slot
from src.domain.schedules.values import SlotTime
from src.domain.users.entities import User, UserPoint
from src.domain.users.values import Email, HumanName, Telephone

TODAY = date(year=2024, month=7, day=8)


@pytest.fixture()
def promotion_20():
    return Promotion(
        code=Name('sale_20'), day_start=TODAY, is_active=True,
        day_end=TODAY + timedelta(days=7), sale=PositiveIntNumber(20)
    )


@pytest.fixture()
def user_ivanov():
    return User(
        email=Email('ivanov@mail.ru'), first_name=HumanName('Ivan'),
        last_name=HumanName('Ivanov'), telephone=Telephone('880005553535')
    )


@pytest.fixture()
def user_petrov():
    return User(
        email=Email('petrov@mail.ru'), first_name=HumanName('Petr'),
        last_name=HumanName('Petrov'), telephone=Telephone('880005553636')
    )


@pytest.fixture()
def ivanov_user_point(user_ivanov):
    return UserPoint(user=user_ivanov, count=CountNumber(700))


@pytest.fixture()
def henna_inventory():
    return Inventory(name=Name('henna'), unit=Name('ml'), stock_count=CountNumber(1000))


@pytest.fixture()
def henna_consumable(henna_inventory):
    return Consumable(inventory=henna_inventory, count=PositiveIntNumber(5))


@pytest.fixture()
def shampoo_inventory():
    return Inventory(name=Name('shampoo'), unit=Name('ml'), stock_count=CountNumber(1000))


@pytest.fixture()
def shampoo_consumable(shampoo_inventory):
    return Consumable(inventory=shampoo_inventory, count=PositiveIntNumber(10))


@pytest.fixture()
def henna_staining_service(henna_consumable, shampoo_consumable):
    return Service(
        consumables=[henna_consumable, shampoo_consumable], name=Name('henna staining'),
        description='includes shampooing and henna staining', price=PositiveIntNumber(1500)
    )


@pytest.fixture()
def henna_master(user_petrov, henna_staining_service):
    return Master(user=user_petrov, services=[henna_staining_service], description='master of henna staining')


@pytest.fixture()
def henna_staining_today_schedule(henna_staining_service, henna_master):
    return Schedule(
        service=henna_staining_service, master=henna_master, day=TODAY
    )


@pytest.fixture()
def henna_staining_today_12_slot(henna_staining_today_schedule):
    return Slot(schedule=henna_staining_today_schedule, time_start=SlotTime("12:00"))


@pytest.fixture()
def henna_staining_today_14_slot(henna_staining_today_schedule):
    return Slot(schedule=henna_staining_today_schedule, time_start=SlotTime("14:00"))
