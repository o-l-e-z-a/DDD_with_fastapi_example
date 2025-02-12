from src.domain.schedules.entities import Order
from src.logic.dto.order_dto import OrderCreateDTO, OrderUpdateDTO, TotalAmountDTO
from src.logic.dto.schedule_dto import ScheduleAddDTO
from src.logic.dto.user_dto import UserCreateDTO, UserLoginDTO
from src.logic.services.schedule_service import ScheduleService, OrderService
from src.logic.services.users_service import UserService
from tests.unit.domain.conftest import *

from .mocs import (
    # FakeConsumablesRepository,
    # FakeInventoryRepository,
    FakeMasterRepository,
    FakeOrderRepository,
    FakeOrderUnitOfWork,
    FakePromotionRepository,
    FakeScheduleRepository,
    FakeScheduleUnitOfWork,
    FakeServiceRepository,
    FakeSlotRepository,
    FakeUserPointRepository,
    FakeUserRepository,
    FakeUsersUnitOfWork,
)


@pytest.fixture()
def fake_user_repo_with_data(user_ivanov, user_petrov):
    fake_user_repo = FakeUserRepository(models=[user_ivanov, user_petrov])
    return fake_user_repo


@pytest.fixture()
def fake_user_point_repo_with_data(ivanov_user_point, petrov_user_point):
    fake_user_point_repo = FakeUserPointRepository(models=[ivanov_user_point, petrov_user_point])
    return fake_user_point_repo


@pytest.fixture()
def user_service_with_data(fake_user_repo_with_data, fake_user_point_repo_with_data):
    fake_uow = FakeUsersUnitOfWork(
        fake_user_repo=fake_user_repo_with_data,
        fake_user_point_repo=fake_user_point_repo_with_data
    )
    return UserService(uow=fake_uow)


@pytest.fixture()
def new_user_dto():
    return UserCreateDTO(
        email='oleg@mail.com',
        first_name='Oleg',
        last_name='Olegov',
        telephone='+79003333333',
        password=PASSWORD,
    )


@pytest.fixture()
def user_ivanov_dto(user_ivanov):
    return UserCreateDTO(
        email=user_ivanov.email.as_generic_type(),
        first_name=user_ivanov.first_name.as_generic_type(),
        last_name=user_ivanov.last_name.as_generic_type(),
        telephone=user_ivanov.telephone.as_generic_type(),
        password=PASSWORD,
    )


@pytest.fixture()
def master_login_dto(user_petrov):
    return UserLoginDTO(
        email=user_petrov.email.as_generic_type(),
        password=PASSWORD,
    )


@pytest.fixture()
def new_user_model(new_user_dto):
    u = User(
        email=Email(new_user_dto.email), first_name=HumanName(new_user_dto.first_name),
        last_name=HumanName(new_user_dto.last_name), telephone=Telephone(new_user_dto.telephone),
    )
    u.id = 3
    return u


@pytest.fixture()
def new_user_point_model(new_user_model):
    return UserPoint(user_id=new_user_model.id)


@pytest.fixture()
def fake_user_repo_with_new_user(fake_user_repo_with_data, new_user_model):
    fake_user_repo_with_data.models.append(new_user_model)
    return fake_user_repo_with_data


@pytest.fixture()
def fake_inventories_repo_with_data(henna_inventory, shampoo_inventory):
    fake_inventories_repo = FakeInventoryRepository(models=[henna_inventory, shampoo_inventory])
    return fake_inventories_repo


@pytest.fixture()
def fake_consumables_repo_with_data(henna_consumable, shampoo_consumable):
    fake_consumables_repo = FakeConsumablesRepository(models=[henna_consumable, shampoo_consumable])
    return fake_consumables_repo


@pytest.fixture()
def fake_service_repo_with_data(henna_staining_service, shampooing_service):
    fake_service_repo = FakeServiceRepository(models=[henna_staining_service, shampooing_service])
    return fake_service_repo


@pytest.fixture()
def fake_masters_repo_with_data(henna_and_shampooing_master):
    fake_masters_repo = FakeMasterRepository(models=[henna_and_shampooing_master])
    return fake_masters_repo


@pytest.fixture()
def fake_schedules_repo_with_data(henna_staining_today_schedule, shampooing_tomorrow_schedule):
    fake_schedules_repo = FakeScheduleRepository(models=[henna_staining_today_schedule, shampooing_tomorrow_schedule])
    return fake_schedules_repo


@pytest.fixture()
def fake_slots_repo_with_data(henna_staining_today_12_slot, henna_staining_today_14_slot):
    fake_slots_repo = FakeSlotRepository(models=[henna_staining_today_12_slot, henna_staining_today_14_slot])
    return fake_slots_repo


@pytest.fixture()
def fake_orders_repo_with_data(henna_staining_today_12_order, henna_staining_today_14_order):
    fake_inventories_repo = FakeOrderRepository(models=[henna_staining_today_12_order, henna_staining_today_14_order])
    return fake_inventories_repo


@pytest.fixture()
def fake_promotions_repo_with_data(promotion_20):
    fake_inventories_repo = FakePromotionRepository(models=[promotion_20])
    return fake_inventories_repo


@pytest.fixture()
def schedule_service_with_data(
    fake_user_repo_with_data, fake_schedules_repo_with_data, fake_slots_repo_with_data,
    fake_consumables_repo_with_data, fake_masters_repo_with_data, fake_service_repo_with_data,
    fake_inventories_repo_with_data
):
    fake_uow = FakeScheduleUnitOfWork(
        fake_users_repo=fake_user_repo_with_data,
        fake_schedules_repo=fake_schedules_repo_with_data,
        fake_slots_repo=fake_slots_repo_with_data,
        fake_consumables_repo=fake_consumables_repo_with_data,
        fake_masters_repo=fake_masters_repo_with_data,
        fake_service_repo=fake_service_repo_with_data,
        fake_inventories_repo=fake_inventories_repo_with_data,
    )
    return ScheduleService(uow=fake_uow)


@pytest.fixture()
def new_schedule_dto(henna_and_shampooing_master, shampooing_service):
    return ScheduleAddDTO(
        day=TODAY,
        service_id=shampooing_service.id,
        master_id=henna_and_shampooing_master.id,
    )


@pytest.fixture()
def new_schedule_model(new_user_dto, new_schedule_dto, henna_and_shampooing_master, shampooing_service):
    u = Schedule(
        day=new_schedule_dto.day,
        master=henna_and_shampooing_master,
        service=shampooing_service,
    )
    u.id = 3
    return u


@pytest.fixture()
def henna_master_days():
    return [TODAY, TOMORROW]


@pytest.fixture()
def order_service_with_data(
    fake_user_repo_with_data, fake_schedules_repo_with_data, fake_slots_repo_with_data,
    fake_consumables_repo_with_data, fake_service_repo_with_data, fake_inventories_repo_with_data,
    fake_promotions_repo_with_data, fake_orders_repo_with_data, fake_user_point_repo_with_data
):
    fake_uow = FakeOrderUnitOfWork(
        fake_users_repo=fake_user_repo_with_data,
        fake_schedules_repo=fake_schedules_repo_with_data,
        fake_slots_repo=fake_slots_repo_with_data,
        fake_consumables_repo=fake_consumables_repo_with_data,
        fake_service_repo=fake_service_repo_with_data,
        fake_inventories_repo=fake_inventories_repo_with_data,
        fake_promotions_repo=fake_promotions_repo_with_data,
        fake_orders_repo=fake_orders_repo_with_data,
        fake_user_point_repo=fake_user_point_repo_with_data,
    )
    return OrderService(uow=fake_uow)


@pytest.fixture()
def new_order_dto(henna_staining_today_schedule):
    total_amount_dto = TotalAmountDTO(
        schedule_id=henna_staining_today_schedule.id,
        point="120",
        promotion_code='sale_20'
    )
    dto = OrderCreateDTO(
        total_amount=total_amount_dto,
        time_start="15:00",
    )
    return dto


@pytest.fixture()
def new_order_model(user_ivanov, henna_staining_today_15_slot):
    u = Order(
        user=user_ivanov,
        slot=henna_staining_today_15_slot,
        point_uses=CountNumber(120),
        promotion_sale=CountNumber(300),
        total_amount=PositiveIntNumber(1080),
    )
    u.id = 3
    return u


@pytest.fixture()
def stock_count_after_order():
    return [995, 990]


@pytest.fixture()
def stock_count_after_delete_order():
    return [1005, 1010]


@pytest.fixture()
def user_point_ivanov_after_order():
    return 580


@pytest.fixture()
def order_update_dto(henna_staining_today_14_order):
    return OrderUpdateDTO(
        order_id=henna_staining_today_14_order.id,
        time_start='18:00'
    )
