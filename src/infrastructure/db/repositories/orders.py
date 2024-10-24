from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from src.infrastructure.db.models.orders import Order
from src.infrastructure.db.models.schedules import Master, Schedule, Service, Slot
from src.infrastructure.db.repositories.base import SQLAlchemyRepository


class OrderRepository(SQLAlchemyRepository[Order]):
    model = Order

    async def get_order_report_by_service(self):
        query = (
            select(
                Service.id,
                Service.name,
                Service.price,
                func.count(Service.id).label("total_count"),
                func.sum(Order.total_amount).label("total_sum"),
            )
            .join(Schedule)
            .join(Slot)
            .join(Order)
            .group_by(Service.id)
        )
        result = await self.session.execute(query)
        return result.mappings().all()

    async def find_one_or_none(self, **filter_by) -> Order | None:
        query = self.get_query_to_find_all(**filter_by)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def find_all(self, **filter_by) -> Sequence[Order]:
        query = self.get_query_to_find_all(**filter_by)
        result = await self.session.execute(query)
        return result.scalars().all()

    # def find_order_by_day(self, day):
    #     user_2 = aliased(Users)
    #     user_1 = aliased(Users)
    #     query = (
    #         select(Order)
    #         .join(Slot).join(Schedule).join(Service).join(Master)
    #         .join(user_1, Master.user_id == user_1.id)
    #         .join(user_2, Order.user_id == user_2.id)
    #         .options(
    #             contains_eager(Order.slot)
    #             .contains_eager(Slot.schedule)
    #             .options(contains_eager(Schedule.service))
    #             .options(contains_eager(Schedule.master).contains_eager(Master.user.of_type(user_1)))
    #         )
    #         .options(contains_eager(Order.user.of_type(user_2)))
    #         .where(Schedule.day == day)
    #     )
    #     result = self.session.execute(query)
    #     return result.scalars().all()

    def get_query_to_find_all(self, **filter_by):
        query = (
            select(self.model)
            .options(
                joinedload(self.model.slot, innerjoin=True)
                .joinedload(Slot.schedule, innerjoin=True)
                .options(joinedload(Schedule.service, innerjoin=True))
                .options(joinedload(Schedule.master, innerjoin=True).joinedload(Master.user, innerjoin=True))
            )
            .options(joinedload(self.model.user, innerjoin=True))
            .filter_by(**filter_by)
        )
        return query

    async def update_photo(self, order: Order, photo_after=None, photo_before=None):
        order.photo_before = photo_before
        order.photo_after = photo_after
        await self.session.commit()
        await self.session.refresh(order)
        return order
