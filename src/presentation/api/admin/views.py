from sqladmin import ModelView

from src.infrastructure.db.models.users import Users, UserPoint
from src.infrastructure.db.models.orders import Promotion, Order
from src.infrastructure.db.models.schedules import Inventory, Consumables, Master, Schedule, Slot, Service


class UsersAdmin(ModelView, model=Users):
    column_exclude_list = [Users.hashed_password]
    column_details_exclude_list = [Users.hashed_password]
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"


class InventoryAdmin(ModelView, model=Inventory):
    column_list = '__all__'


class ConsumablesAdmin(ModelView, model=Consumables):
    column_list = '__all__'


class ServiceAdmin(ModelView, model=Service):
    column_list = '__all__'


class MasterAdmin(ModelView, model=Master):
    column_list = '__all__'


class SlotAdmin(ModelView, model=Slot):
    column_list = '__all__'


class ScheduleAdmin(ModelView, model=Schedule):
    column_list = '__all__'


class UserPointAdmin(ModelView, model=UserPoint):
    column_list = '__all__'


class PromotionAdmin(ModelView, model=Promotion):
    column_list = '__all__'


class OrderAdmin(ModelView, model=Order):
    column_list = '__all__'
