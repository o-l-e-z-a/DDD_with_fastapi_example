from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Column, ForeignKey, String, Integer
from sqlalchemy.ext.hybrid import hybrid_property
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


class Promotion(Base[entities.Promotion]):
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
            [service.to_domain(with_join=with_join_to_child, child_level=child_level).id for service in self.services]
            if with_join
            else []
        )
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

    user: Mapped["Users"] = relationship(back_populates="points")

    __table_args__ = (CheckConstraint("count >= 0", name="check_count_positive"),)

    def to_domain(self, with_join: bool = False, child_level: int = 0) -> entities.UserPoint:
        with_join_to_child, child_level = get_child_join_and_level(with_join=with_join, child_level=child_level)
        user = self.user.to_domain(with_join=with_join_to_child, child_level=child_level) if with_join else None
        user_point = entities.UserPoint(
            count=CountNumber(self.count),
            user_id=self.user_id,
        )
        user_point.id = self.id
        return user_point

    @classmethod
    def from_entity(cls, entity: entities.UserPoint) -> UserPoint:
        return cls(
            id=getattr(entity, "id", None),
            count=entity.count.as_generic_type(),
            user_id=entity.user_id
        )

