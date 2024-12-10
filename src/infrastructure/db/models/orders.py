from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String, Column

# from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_file import ImageField

from src.domain.base.values import CountNumber, Name, PositiveIntNumber
from src.domain.orders import entities
from src.infrastructure.db.models.base import Base, get_child_join_and_level, int_pk

if TYPE_CHECKING:
    from src.infrastructure.db.models.schedules import Service, Slot
    from src.infrastructure.db.models.users import Users


POINT_AFTER_ORDER = 50


class PromotionToService(Base):
    __tablename__ = "promotion_to_service"

    promotion_id: Mapped[int] = mapped_column(
        ForeignKey("promotion.id", ondelete="CASCADE"),
        primary_key=True,
    )
    service_id: Mapped[int] = mapped_column(
        ForeignKey("service.id", ondelete="CASCADE"),
        primary_key=True,
    )


class Promotion(Base):
    __tablename__ = "promotion"

    id: Mapped[int_pk]
    code: Mapped[str] = mapped_column(String(15), unique=True)
    sale: Mapped[int]
    is_active: Mapped[bool] = mapped_column(server_default="f", default=False)
    day_start: Mapped[date] = mapped_column(default=date.today())
    day_end: Mapped[date]
    services: Mapped[list["Service"]] = relationship(secondary="promotion_to_service")

    __table_args__ = (CheckConstraint("sale > 0 AND sale < 100", name="check_sale_percent"),)

    def to_domain(self, with_join: bool = False, child_level: int = 0) -> entities.Promotion:
        with_join_to_child, child_level = get_child_join_and_level(with_join=with_join, child_level=child_level)
        services = (
            [service.to_domain(with_join=with_join_to_child, child_level=child_level) for service in self.services]
            if with_join
            else []
        )
        promotion = entities.Promotion(
            code=Name(self.code),
            sale=PositiveIntNumber(self.sale),
            is_active=self.is_active,
            day_start=self.day_start,
            day_end=self.day_end,
            services=services,
        )
        promotion.id = self.id
        return promotion

    @classmethod
    def from_entity(cls, entity: entities.Promotion) -> Promotion:
        return cls(
            id=getattr(entity, "id", None),
            code=entity.code.as_generic_type(),
            sale=entity.sale.as_generic_type(),
            is_active=entity.is_active,
            day_start=entity.day_start,
            day_end=entity.day_end,
        )


class Order(Base):
    __tablename__ = "order"

    id: Mapped[int_pk]
    slot_id: Mapped[int] = mapped_column(ForeignKey("slot.id", ondelete="CASCADE"), unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    point_uses: Mapped[int] = mapped_column(default=0)
    promotion_sale: Mapped[int] = mapped_column(default=0)
    total_amount: Mapped[int] = mapped_column(default=0)
    date_add: Mapped[date] = mapped_column(default=date.today())
    photo_before = Column(ImageField)
    photo_after = Column(ImageField)
    # photo_after = models.ImageField('Фото после', upload_to='photo_after/', blank=True, null=True)

    slot: Mapped["Slot"] = relationship(back_populates="order")
    user: Mapped["Users"] = relationship()

    __table_args__ = (
        CheckConstraint("point_uses >= 0", name="check_point_uses_positive"),
        CheckConstraint("promotion_sale >= 0", name="check_promotion_sale_positive"),
        CheckConstraint("total_amount >= 0", name="check_total_amount_positive"),
    )

    def to_domain(self, with_join: bool = False, child_level: int = 0) -> entities.Order:
        with_join_to_child, child_level = get_child_join_and_level(with_join=with_join, child_level=child_level)
        user = self.user.to_domain(with_join=with_join_to_child, child_level=child_level) if with_join else None
        slot = self.slot.to_domain(with_join=with_join_to_child, child_level=child_level) if with_join else None
        order = entities.Order(
            point_uses=CountNumber(self.point_uses),
            promotion_sale=CountNumber(self.promotion_sale),
            total_amount=PositiveIntNumber(self.total_amount),
            user=user,
            slot=slot,
            date_add=self.date_add,
        )
        order.id = self.id
        return order

    @classmethod
    def from_entity(cls, entity: entities.Order) -> Order:
        return cls(
            id=getattr(entity, "id", None),
            slot_id=entity.slot.id,
            user_id=entity.user.id,
            point_uses=entity.point_uses.as_generic_type(),
            promotion_sale=entity.promotion_sale.as_generic_type(),
            total_amount=entity.total_amount.as_generic_type(),
        )
