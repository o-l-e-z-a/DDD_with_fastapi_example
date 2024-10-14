from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import EmailType

from src.domain.users import entities
from src.domain.users.values import Email, HumanName, Telephone
from src.infrastructure.db.models.base import Base, created_at, int_pk, updated_at

if TYPE_CHECKING:
    from src.infrastructure.db.models.schedules import Master


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int_pk]
    email: Mapped[str] = mapped_column(EmailType, unique=True)
    hashed_password: Mapped[str]
    first_name: Mapped[str]
    last_name: Mapped[str]
    telephone: Mapped[str] = mapped_column(unique=True)
    date_birthday: Mapped[date] = mapped_column(Date, nullable=True)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    is_active: Mapped[bool] = mapped_column(server_default="t", default=True)
    is_superuser: Mapped[bool] = mapped_column(server_default="f", default=False)

    master: Mapped["Master"] = relationship(
        back_populates="user",
    )
    points: Mapped[list["UserPoint"]] = relationship(back_populates="user")

    def to_domain(self) -> entities.User:
        user = entities.User(
            email=Email(self.email),
            first_name=HumanName(self.first_name),
            last_name=HumanName(self.last_name),
            telephone=Telephone(self.telephone),
            date_birthday=self.date_birthday,
        )
        user.id = self.id
        return user

    def __repr__(self):
        return f"User c id: {id}, email: {self.email}"


class UserPoint(Base):
    __tablename__ = "user_point"

    id: Mapped[int_pk]
    count: Mapped[int] = mapped_column(Integer, default=0)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)

    user: Mapped[Users] = relationship(back_populates="points")

    __table_args__ = (CheckConstraint("count >= 0", name="check_count_positive"),)

    def to_domain(self) -> entities.UserPoint:
        user_point = entities.UserPoint(
            count=self.count,
            user=self.user,
        )
        user_point.id = self.id
        return user_point
