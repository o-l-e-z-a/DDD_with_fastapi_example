from __future__ import annotations

from datetime import date, time
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.base.values import Name, PositiveIntNumber
from src.domain.schedules import entities
from src.domain.schedules.values import SlotTime
from src.infrastructure.db.models.base import Base, get_child_join_and_level, int_pk, str_255
from src.infrastructure.db.models.orders import Order

if TYPE_CHECKING:
    from src.infrastructure.db.models.users import Users


# class Inventory(Base[entities.Inventory]):
#     __tablename__ = "inventory"
#
#     id: Mapped[int_pk]
#     name: Mapped[str] = mapped_column(String(50))
#     unit: Mapped[str] = mapped_column(String(50))
#     stock_count: Mapped[int]
#
#     consumables: Mapped[list["Consumables"]] = relationship(back_populates="inventory")
#
#     def to_domain(self, with_join: bool = False, child_level: int = 0) -> entities.Inventory:
#         inventory = entities.Inventory(
#             name=Name(self.name), unit=Name(self.unit), stock_count=CountNumber(self.stock_count)
#         )
#         inventory.id = self.id
#         return inventory
#
#     @classmethod
#     def from_entity(cls, entity: entities.Inventory) -> Inventory:
#         return cls(
#             id=getattr(entity, "id", None),
#             name=entity.name.as_generic_type(),
#             unit=entity.unit.as_generic_type(),
#             stock_count=entity.stock_count.as_generic_type(),
#         )
#
#
# class ConsumableToService(Base):
#     __tablename__ = "consumable_to_service"
#
#     consumable_id: Mapped[int] = mapped_column(
#         ForeignKey("consumable.id", ondelete="CASCADE"),
#         primary_key=True,
#     )
#     service_id: Mapped[int] = mapped_column(
#         ForeignKey("service.id", ondelete="CASCADE"),
#         primary_key=True,
#     )

#
# class Consumables(Base):
#     __tablename__ = "consumable"
#
#     id: Mapped[int_pk]
#     inventory_id: Mapped[int] = mapped_column(ForeignKey("inventory.id", ondelete="CASCADE"))
#     inventory: Mapped["Inventory"] = relationship(back_populates="consumables")
#     count: Mapped[int]
#     services: Mapped[list["Service"]] = relationship(back_populates="consumables", secondary="consumable_to_service")
#
#     __table_args__ = (CheckConstraint("count >= 0", name="check_count_positive"),)
#
#     def to_domain(self, with_join: bool = False, child_level: int = 0) -> entities.Consumable:
#         with_join_to_child, child_level = get_child_join_and_level(with_join=with_join, child_level=child_level)
#         inventory = (
#             self.inventory.to_domain(with_join=with_join_to_child, child_level=child_level) if with_join else None
#         )
#         consumable = entities.Consumable(
#             inventory=inventory,
#             count=PositiveIntNumber(self.count),
#         )
#         consumable.id = self.id
#         return consumable
#
#     @classmethod
#     def from_entity(cls, entity: entities.Consumable) -> Consumables:
#         return cls(
#             id=getattr(entity, "id", None), count=entity.count.as_generic_type(), inventory_id=entity.inventory.id
#         )


class Service(Base):
    __tablename__ = "service"

    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str]
    price: Mapped[int]

    # consumables: Mapped[list["Consumables"]] = relationship(
    #     back_populates="services", secondary="consumable_to_service"
    # )
    masters: Mapped[list["Master"]] = relationship(
        back_populates="services",
        secondary="service_to_master",
    )
    schedules: Mapped[list["Schedule"]] = relationship(
        back_populates="service",
    )

    __table_args__ = (CheckConstraint("price >= 0", name="check_count_positive"),)

    def to_domain(self, with_join: bool = False, child_level: int = 0) -> entities.Service:
        with_join_to_child, child_level = get_child_join_and_level(with_join=with_join, child_level=child_level)
        # consumables = (
        #     [
        #         consumable.to_domain(with_join=with_join_to_child, child_level=child_level)
        #         for consumable in self.consumables
        #     ]
        #     if with_join
        #     else []
        # )
        service = entities.Service(
            name=Name(self.name),
            description=self.description,
            price=PositiveIntNumber(self.price),
            # consumables=consumables,
        )
        service.id = self.id
        return service

    @classmethod
    def from_entity(cls, entity: entities.Service) -> Service:
        return cls(
            id=getattr(entity, "id", None),
            name=entity.name.as_generic_type(),
            description=entity.description,
            price=entity.price.as_generic_type(),
        )

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

    def to_domain(self, with_join: bool = False, child_level: int = 0) -> entities.Master:
        with_join_to_child, child_level = get_child_join_and_level(with_join=with_join, child_level=child_level)
        services = (
            [service.to_domain(with_join=with_join_to_child, child_level=child_level) for service in self.services]
            if with_join
            else []
        )
        user = self.user.to_domain(with_join=with_join_to_child, child_level=child_level) if with_join else None
        master = entities.Master(
            description=self.description,
            user=user,
            services=services,
        )
        master.id = self.id
        return master

    @classmethod
    def from_entity(cls, entity: entities.Master) -> Master:
        return cls(id=getattr(entity, "id", None), description=entity.description, user_id=entity.user.id)

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

    def to_domain(self, with_join: bool = False, child_level: int = 0) -> entities.Schedule:
        with_join_to_child, child_level = get_child_join_and_level(with_join=with_join, child_level=child_level)
        master = self.master.to_domain(with_join=with_join_to_child, child_level=child_level) if with_join else None
        service = self.service.to_domain(with_join=with_join_to_child, child_level=child_level) if with_join else None
        schedule = entities.Schedule(
            master=master,
            service=service,
            day=self.day,
        )
        schedule.id = self.id
        return schedule

    @classmethod
    def from_entity(cls, entity: entities.Schedule) -> Schedule:
        return cls(
            id=getattr(entity, "id", None), day=entity.day, master_id=entity.master.id, service_id=entity.service.id
        )


class Slot(Base):
    __tablename__ = "slot"

    id: Mapped[int_pk]
    time_start: Mapped[time]
    time_end: Mapped[time] = mapped_column(nullable=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("schedule.id", ondelete="CASCADE"))

    schedule: Mapped["Schedule"] = relationship(back_populates="slots")
    order: Mapped["Order"] = relationship(back_populates="slot")

    __table_args__ = (UniqueConstraint("schedule_id", "time_start"),)

    def to_domain(self, with_join: bool = False, child_level: int = 0) -> entities.Slot:
        with_join_to_child, child_level = get_child_join_and_level(with_join=with_join, child_level=child_level)
        schedule = self.schedule.to_domain(with_join=with_join_to_child, child_level=child_level) if with_join else None
        slot = entities.Slot(
            time_start=SlotTime(str(self.time_start.strftime("%H:%M"))),
            schedule=schedule,
        )
        slot.id = self.id
        return slot

    @classmethod
    def from_entity(cls, entity: entities.Slot) -> Slot:
        return cls(
            id=getattr(entity, "id", None),
            time_start=time.fromisoformat(entity.time_start.as_generic_type()),
            schedule_id=entity.schedule.id,
        )
