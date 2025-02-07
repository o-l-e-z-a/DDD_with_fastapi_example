from __future__ import annotations

from datetime import date, time, datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint, Column
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_file import ImageField

from src.domain.base.values import Name, PositiveIntNumber, CountNumber
from src.domain.schedules import entities
from src.domain.schedules.values import SlotTime
from src.infrastructure.db.models.base import Base, get_child_join_and_level, int_pk, str_255

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
    orders: Mapped[list["Order"]] = relationship(
        back_populates="service",
    )
    masters: Mapped[list["Master"]] = relationship(
        back_populates="services",
        secondary="service_to_master",
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
        services_id = (
            [service.id for service in self.services]
            if with_join
            else []
        )
        master = entities.Master(
            description=self.description,
            user_id=self.user_id,
            services_id=services_id,
        )
        master.id = self.id
        return master

    @classmethod
    def from_entity(cls, entity: entities.Master) -> Master:
        return cls(id=getattr(entity, "id", None), description=entity.description, user_id=entity.user_id)

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

    slots: Mapped[list["Slot"]] = relationship(back_populates="schedule")
    master: Mapped["Master"] = relationship(back_populates="schedules")

    __table_args__ = (UniqueConstraint("day", "master_id"),)

    def to_domain(self, with_join: bool = False, child_level: int = 0) -> entities.Schedule:
        with_join_to_child, child_level = get_child_join_and_level(with_join=with_join, child_level=child_level)
        # master = self.master.to_domain(with_join=with_join_to_child, child_level=child_level) if with_join else None
        slots = [
            slot.to_domain(with_join=with_join_to_child, child_level=child_level) for slot in self.slots
        ] if with_join else []
        schedule = entities.Schedule(
            master_id=self.master_id,
            slots=slots,
            day=self.day,
        )
        schedule.id = self.id
        return schedule

    @classmethod
    def from_entity(cls, entity: entities.Schedule) -> Schedule:
        return cls(
            id=getattr(entity, "id", None),
            day=entity.day,
            master_id=entity.master_id,
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
        # with_join_to_child, child_level = get_child_join_and_level(with_join=with_join, child_level=child_level)
        # schedule = self.schedule.to_domain(with_join=with_join_to_child, child_level=child_level) if with_join else None
        slot = entities.Slot(
            time_start=SlotTime(str(self.time_start.strftime("%H:%M"))),
        )
        slot.id = self.id
        slot.schedule_id = self.schedule_id

        return slot

    @classmethod
    def from_entity(cls, entity: entities.Slot, **kwargs) -> Slot:
        return cls(
            id=getattr(entity, "id", None),
            time_start=time.fromisoformat(entity.time_start.as_generic_type()),
            # schedule_id=entity.schedule_id,
        )


class Order(Base):
    __tablename__ = "order"

    id: Mapped[int_pk]
    slot_id: Mapped[int] = mapped_column(ForeignKey("slot.id", ondelete="CASCADE"), unique=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("service.id", ondelete="CASCADE"), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    # point_uses: Mapped[int] = mapped_column(default=0)
    # promotion_sale: Mapped[int] = mapped_column(default=0)
    # total_amount: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(nullable=True)
    date_add: Mapped[datetime] = mapped_column(default=datetime.today())
    photo_after = Column(ImageField)
    photo_before = Column(ImageField)

    slot: Mapped["Slot"] = relationship(back_populates="order")
    service: Mapped["Service"] = relationship(back_populates="orders")
    user: Mapped["Users"] = relationship()

    # __table_args__ = (
    #     CheckConstraint("point_uses >= 0", name="check_point_uses_positive"),
    #     CheckConstraint("promotion_sale >= 0", name="check_promotion_sale_positive"),
    #     CheckConstraint("total_amount >= 0", name="check_total_amount_positive"),
    # )

    @hybrid_property
    def photo_before_path(self):
        if self.photo_before:
            return "media/" + self.photo_before.get("path", "")

    @hybrid_property
    def photo_after_path(self):
        if self.photo_after:
            return "media/" + self.photo_after.get("path", "")

    def to_domain(self, with_join: bool = False, child_level: int = 0) -> entities.Order:
        # with_join_to_child, child_level = get_child_join_and_level(with_join=with_join, child_level=child_level)
        # user = self.user.to_domain(with_join=with_join_to_child, child_level=child_level) if with_join else None
        # slot = self.slot.to_domain(with_join=with_join_to_child, child_level=child_level) if with_join else None
        order = entities.Order(
            # point_uses=CountNumber(self.point_uses),
            # promotion_sale=CountNumber(self.promotion_sale),
            # total_amount=PositiveIntNumber(self.total_amount),
            photo_before_path=self.photo_before_path,
            photo_after_path=self.photo_after_path,
            user_id=self.user_id,
            slot_id=self.slot_id,
            service_id=self.service_id,
            date_add=self.date_add,
        )
        order.id = self.id
        return order

    @classmethod
    def from_entity(cls, entity: entities.Order) -> Order:
        return cls(
            id=getattr(entity, "id", None),
            slot_id=entity.slot_id,
            user_id=entity.user_id,
            service_id=entity.service_id,
            # point_uses=entity.point_uses.as_generic_type(),
            # promotion_sale=entity.promotion_sale.as_generic_type(),
            # total_amount=entity.total_amount.as_generic_type(),
            photo_before=entity.photo_before_path,
            photo_after=entity.photo_after_path,
        )
