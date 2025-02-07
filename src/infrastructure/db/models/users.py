from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import EmailType

from src.domain.base.values import CountNumber
from src.domain.users import entities
from src.domain.users.values import Email, HumanName, Telephone
from src.infrastructure.db.models.base import Base, created_at, get_child_join_and_level, int_pk, updated_at

if TYPE_CHECKING:
    from src.infrastructure.db.models.schedules import Master
    from src.infrastructure.db.models.orders import UserPoint


class Users(Base[entities.User]):
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

    def to_domain(self, with_join: bool = False, child_level: int = 0) -> entities.User:
        user = entities.User(
            email=Email(self.email),
            first_name=HumanName(self.first_name),
            last_name=HumanName(self.last_name),
            telephone=Telephone(self.telephone),
            date_birthday=self.date_birthday,
            is_admin=self.is_superuser
        )
        user.hashed_password = self.hashed_password
        user.id = self.id
        return user

    @classmethod
    def from_entity(cls, entity: entities.User) -> Users:
        return cls(
            id=getattr(entity, "id", None),
            email=entity.email.as_generic_type(),
            hashed_password=entity.hashed_password,
            first_name=entity.first_name.as_generic_type(),
            last_name=entity.last_name.as_generic_type(),
            telephone=entity.telephone.as_generic_type(),
            date_birthday=entity.date_birthday,
            is_superuser=entity.is_admin,
        )

    def __repr__(self):
        return f"User c id: {self.id}, email: {self.email}"
