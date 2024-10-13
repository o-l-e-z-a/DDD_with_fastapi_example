from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String

# from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.db.models.base import Base, int_pk
from src.infrastructure.db.models.schedules import Slot
from src.infrastructure.db.models.users import Users

if TYPE_CHECKING:
    from src.infrastructure.db.models.schedules import Service

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


class Order(Base):
    __tablename__ = "order"

    id: Mapped[int_pk]
    slot_id: Mapped[int] = mapped_column(ForeignKey("slot.id", ondelete="CASCADE"), unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    point_uses: Mapped[int] = mapped_column(default=0)
    promotion_sale: Mapped[int] = mapped_column(default=0)
    total_amount: Mapped[int] = mapped_column(default=0)
    date_add: Mapped[date] = mapped_column(default=date.today())
    # photo_before = Column(ImageField)
    # photo_after = models.ImageField('Фото после', upload_to='photo_after/', blank=True, null=True)

    slot: Mapped["Slot"] = relationship(back_populates="order")
    user: Mapped["Users"] = relationship()

    __table_args__ = (
        CheckConstraint("point_uses >= 0", name="check_point_uses_positive"),
        CheckConstraint("promotion_sale >= 0", name="check_promotion_sale_positive"),
        CheckConstraint("total_amount >= 0", name="check_total_amount_positive"),
    )
    #
    # @hybrid_property
    # def photo_before_path(self):
    #     if self.photo_before:
    #         return self.photo_before.get('url', None)
