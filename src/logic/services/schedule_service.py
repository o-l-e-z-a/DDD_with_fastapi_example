from typing import Sequence

from src.domain.schedules.entities import Service
from src.logic.uows.schedule_uow import SQLAlchemyScheduleUnitOfWork


class ScheduleService:
    def __init__(self, uow: SQLAlchemyScheduleUnitOfWork):
        self.uow = uow

    async def get_services(self) -> Sequence[Service]:
        async with self.uow:
            user_point = await self.uow.services.find_all()
        return user_point
