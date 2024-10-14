from datetime import date, time
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.db.models.base import Base, int_pk, str_255

if TYPE_CHECKING:
    from src.infrastructure.db.models import Order
    from src.infrastructure.db.models.users import Users


class Inventory(Base):
    __tablename__ = "inventory"

    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(String(50))
    unit: Mapped[str] = mapped_column(String(50))
    stock_count: Mapped[int]

    consumables: Mapped[list["Consumables"]] = relationship(back_populates="inventory")


class ConsumableToInventory(Base):
    __tablename__ = "consumable_to_inventory"

    consumable_id: Mapped[int] = mapped_column(
        ForeignKey("consumable.id", ondelete="CASCADE"),
        primary_key=True,
    )
    service_id: Mapped[int] = mapped_column(
        ForeignKey("service.id", ondelete="CASCADE"),
        primary_key=True,
    )


class Consumables(Base):
    __tablename__ = "consumable"

    id: Mapped[int_pk]
    inventory_id: Mapped[int] = mapped_column(ForeignKey("inventory.id", ondelete="CASCADE"))
    inventory: Mapped["Inventory"] = relationship(back_populates="consumables")
    count: Mapped[int]
    services: Mapped[list["Service"]] = relationship(back_populates="consumables", secondary="consumable_to_inventory")

    __table_args__ = (CheckConstraint("count >= 0", name="check_count_positive"),)

    # def __repr__(self):
    #     return f'{self.inventory.name}: {self.count}'


class Service(Base):
    __tablename__ = "service"

    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str]
    price: Mapped[int]
    # photo = models.ImageField('Фото услуги', upload_to='service_photo/', blank=True, null=True)

    consumables: Mapped[list["Consumables"]] = relationship(
        back_populates="services", secondary="consumable_to_inventory"
    )
    masters: Mapped[list["Master"]] = relationship(
        back_populates="services",
        secondary="service_to_master",
    )
    schedules: Mapped[list["Schedule"]] = relationship(
        back_populates="service",
    )

    __table_args__ = (CheckConstraint("price >= 0", name="check_count_positive"),)

    def __repr__(self):
        return f"{self.name} - {self.price}"


class Master(Base):
    __tablename__ = "master"

    id: Mapped[int_pk]
    description: Mapped[str_255]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    # photo = models.ImageField('Фото мастера', upload_to='service_photo/', blank=True, null=True)

    user: Mapped["Users"] = relationship(back_populates="master")
    services: Mapped[list["Service"]] = relationship(
        back_populates="masters",
        secondary="service_to_master",
    )
    schedules: Mapped[list["Schedule"]] = relationship(
        back_populates="master",
    )

    __table_args__ = (UniqueConstraint("user_id"),)

    # def __repr__(self):
    # return f'{self.user.last_name} {self.user.first_name} , {self.user.email}'
    # return f'{self.id} {self.description} , {self.user_id}'


class ServiceToMaster(Base):
    __tablename__ = "service_to_master"

    master_id: Mapped[int] = mapped_column(
        ForeignKey("master.id", ondelete="CASCADE"),
        primary_key=True,
    )
    service_id: Mapped[int] = mapped_column(
        ForeignKey("service.id", ondelete="CASCADE"),
        primary_key=True,
    )


class Schedule(Base):
    __tablename__ = "schedule"

    id: Mapped[int_pk]
    day: Mapped[date]
    master_id: Mapped[int] = mapped_column(ForeignKey("master.id", ondelete="CASCADE"))
    service_id: Mapped[int] = mapped_column(ForeignKey("service.id", ondelete="CASCADE"))

    slots: Mapped[list["Slot"]] = relationship(back_populates="schedule")
    master: Mapped["Master"] = relationship(back_populates="schedules")
    service: Mapped["Service"] = relationship(back_populates="schedules")

    __table_args__ = (UniqueConstraint("day", "master_id", "service_id"),)


class Slot(Base):
    __tablename__ = "slot"

    id: Mapped[int_pk]
    time_start: Mapped[time]
    time_end: Mapped[time] = mapped_column(nullable=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("schedule.id", ondelete="CASCADE"))

    schedule: Mapped["Schedule"] = relationship(back_populates="slots")
    order: Mapped["Order"] = relationship(back_populates="slot")

    __table_args__ = (UniqueConstraint("schedule_id", "time_start"),)
