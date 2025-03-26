from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.base.values import CountNumber, Name, PositiveIntNumber
from src.domain.orders import entities
from src.infrastructure.db.models.base import Base, int_pk

if TYPE_CHECKING:
    pass


POINT_AFTER_ORDER = 50


class PromotionToService(Base):
    __tablename__ = "promotion_to_service"

    promotion_id: Mapped[int] = mapped_column(
        ForeignKey("promotion.id", ondelete="CASCADE"),
        primary_key=True,
    )
    service_id: Mapped[int_pk]


class Promotion(Base[entities.Promotion]):
    __tablename__ = "promotion"

    id: Mapped[int_pk]
    code: Mapped[str] = mapped_column(String(15), unique=True)
    sale: Mapped[int]
    is_active: Mapped[bool] = mapped_column(server_default="f", default=False)
    day_start: Mapped[date] = mapped_column(default=date.today())
    day_end: Mapped[date]
    services: Mapped[list["PromotionToService"]] = relationship(PromotionToService)

    __table_args__ = (CheckConstraint("sale > 0 AND sale < 100", name="check_sale_percent"),)

    def to_domain(self) -> entities.Promotion:
        services = [service.service_id for service in self.services]
        promotion = entities.Promotion(
            code=Name(self.code),
            sale=PositiveIntNumber(self.sale),
            is_active=self.is_active,
            day_start=self.day_start,
            day_end=self.day_end,
            services_id=services,
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


class UserPoint(Base[entities.UserPoint]):
    __tablename__ = "user_point"

    id: Mapped[int_pk]
    count: Mapped[int] = mapped_column(Integer, default=0)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)

    # user: Mapped["Users"] = relationship(back_populates="points")

    __table_args__ = (CheckConstraint("count >= 0", name="check_count_positive"),)

    def to_domain(self) -> entities.UserPoint:
        user_point = entities.UserPoint(
            count=CountNumber(self.count),
            user_id=self.user_id,
        )
        user_point.id = self.id
        return user_point

    @classmethod
    def from_entity(cls, entity: entities.UserPoint) -> UserPoint:
        return cls(id=getattr(entity, "id", None), count=entity.count.as_generic_type(), user_id=entity.user_id)


class OrderPayment(Base[entities.OrderPayment]):
    __tablename__ = "order_payment"

    id: Mapped[int_pk]
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id", ondelete="CASCADE"), unique=True)
    total_amount: Mapped[int] = mapped_column(Integer)
    point_uses: Mapped[int] = mapped_column(Integer, default=0)
    promotion_sale: Mapped[int] = mapped_column(Integer, default=0)
    is_payed: Mapped[bool] = mapped_column(server_default="f", default=False)

    # order: Mapped["Order"] = relationship()

    __table_args__ = (
        CheckConstraint("point_uses >= 0", name="check_point_uses_positive"),
        CheckConstraint("promotion_sale >= 0", name="check_promotion_sale_positive"),
        CheckConstraint("total_amount > 0", name="check_total_amount_positive"),
    )

    def to_domain(self) -> entities.OrderPayment:
        order_payment = entities.OrderPayment(
            point_uses=CountNumber(self.point_uses),
            promotion_sale=CountNumber(self.promotion_sale),
            total_amount=PositiveIntNumber(self.total_amount),
            is_payed=self.is_payed,
            order_id=self.order_id,
        )
        order_payment.id = self.id
        return order_payment

    @classmethod
    def from_entity(cls, entity: entities.OrderPayment) -> OrderPayment:
        return cls(
            id=getattr(entity, "id", None),
            total_amount=entity.total_amount.as_generic_type(),
            point_uses=entity.point_uses.as_generic_type(),
            promotion_sale=entity.promotion_sale.as_generic_type(),
            is_payed=entity.is_payed,
            order_id=entity.order_id,
        )
