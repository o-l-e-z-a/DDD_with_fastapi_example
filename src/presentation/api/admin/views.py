from sqladmin import ModelView

from src.infrastructure.db.models.orders import Promotion, UserPoint
from src.infrastructure.db.models.schedules import Master, Schedule, Service, Slot, Order
from src.infrastructure.db.models.users import Users


class UsersAdmin(ModelView, model=Users):  # type: ignore[call-arg]
    column_exclude_list = [Users.hashed_password]
    column_details_exclude_list = [Users.hashed_password]
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid  fa-user"


class ServiceAdmin(ModelView, model=Service):  # type: ignore[call-arg]
    column_list = "__all__"


class MasterAdmin(ModelView, model=Master):  # type: ignore[call-arg]
    column_list = "__all__"


class SlotAdmin(ModelView, model=Slot):  # type: ignore[call-arg]
    column_list = "__all__"


class ScheduleAdmin(ModelView, model=Schedule):  # type: ignore[call-arg]
    column_list = "__all__"


class UserPointAdmin(ModelView, model=UserPoint):  # type: ignore[call-arg]
    column_list = "__all__"


class PromotionAdmin(ModelView, model=Promotion):  # type: ignore[call-arg]
    column_list = "__all__"


class OrderAdmin(ModelView, model=Order):  # type: ignore[call-arg]
    column_list = "__all__"
