from datetime import date
from typing import Sequence

from sqlalchemy import extract, func, select
from sqlalchemy.orm import joinedload, selectinload

from src.infrastructure.db.models.orders import Order
from src.infrastructure.db.models.schedules import Consumables, Inventory, Master, Schedule, Service, Slot
from src.infrastructure.db.models.users import Users
from src.infrastructure.db.repositories.base import SQLAlchemyRepository


class InventoryRepository(SQLAlchemyRepository[Inventory]):
    model = Inventory


class ConsumablesRepository(SQLAlchemyRepository[Consumables]):
    model = Consumables


class ServiceRepository(SQLAlchemyRepository[Service]):
    model = Service

    async def get_services_by_ids(self, ids: list[int]) -> Sequence[Service]:
        query = select(self.model).where(self.model.id.in_(ids))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_service_with_consumable(self, service_id: int) -> Service | None:
        query = (
            select(self.model)
            .options(selectinload(self.model.consumables).joinedload(Consumables.inventory))
            .where(self.model.id == service_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class MasterRepository(SQLAlchemyRepository[Master]):
    model = Master

    async def get_users_to_masters(self) -> Sequence[Users]:
        query = select(Users).where(~Users.master.has())
        result = await self.session.execute(query)
        return result.scalars().all()

    async def find_all(self, **filter_by) -> Sequence[Master]:
        query = (
            select(self.model)
            .options(joinedload(self.model.user))
            .options(selectinload(self.model.services))
            .filter_by(**filter_by)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    # async def add(self, description: str, user_id: int, services: Sequence[Service], **data) -> int:
    #     # async def add(self, **data) -> int:
    #     master = Master(user_id=user_id, description=description, services=services)
    #     self.session.add(master)
    #     await self.session.commit()
    #     return master.id

    async def find_one_or_none(self, **filter_by) -> Master | None:
        query = (
            select(self.model)
            .options(joinedload(self.model.user))
            .options(selectinload(self.model.services))
            .filter_by(**filter_by)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def filter_by_service(self, service_pk: int) -> Sequence[Master]:
        query = (
            select(self.model)
            .options(joinedload(self.model.user))
            .options(selectinload(self.model.services))
            .where(Service.id == service_pk)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_order_report_by_master(self, month: int | None = None):
        month = month if month else date.today().month
        master_with_reports = (
            select(
                Master.id,
                Master.user_id,
                func.count(Master.id).label("total_count"),
                func.sum(Order.total_amount).label("total_sum"),
            )
            .join(Schedule)
            .join(Slot)
            .join(Order)
            .join(Service)
            .where(extract("month", Order.date_add) == month)
            .group_by(Master.id)
            .cte("master_with_reports")
        )
        query = (
            select(
                Users.last_name,
                Users.first_name,
                master_with_reports.c.total_count,
                master_with_reports.c.total_sum,
                master_with_reports.c.id,
            )
            .select_from(Users)
            .join(master_with_reports, master_with_reports.c.user_id == Users.id)
        )
        result = await self.session.execute(query)
        return result.mappings().all()


class ScheduleRepository(SQLAlchemyRepository[Schedule]):
    model = Schedule

    async def find_all(self, **filter_by) -> Sequence[Schedule]:
        query = (
            select(self.model)
            .options(joinedload(self.model.master).joinedload(Master.user))
            .options(joinedload(self.model.service))
            .filter_by(**filter_by)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def find_one_or_none(self, **filter_by) -> Schedule | None:
        query = (
            select(self.model)
            .options(joinedload(self.model.master).joinedload(Master.user))
            .options(joinedload(self.model.service))
            .filter_by(**filter_by)
        )
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def get_day_for_master(self, **filter_by) -> Sequence[date]:
        query = select(self.model.day.distinct()).filter_by(**filter_by)
        execute_result = await self.session.execute(query)
        result = execute_result.scalars().all()
        return result


class SlotRepository(SQLAlchemyRepository[Slot]):
    model = Slot

    async def find_one_or_none(self, **filter_by) -> Slot | None:
        query = select(self.model).join(Schedule).filter_by(**filter_by)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def find_all(self, **filter_by) -> Sequence[Slot]:
        query = select(self.model).join(Schedule).filter_by(**filter_by)
        result = await self.session.execute(query)
        return result.scalars().all()
