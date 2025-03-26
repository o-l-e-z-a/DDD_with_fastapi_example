import asyncio
import datetime

from sqlalchemy.ext.asyncio import async_sessionmaker

from src.infrastructure.db.models.orders import Promotion, PromotionToService
from src.presentation.api.dependencies import setup_container


async def add_promotion():
    container = setup_container()
    session_factory = await container.get(async_sessionmaker)
    async with session_factory() as session:
        # query = select(Slot, Schedule).join(Schedule).filter_by(day=datetime.date(year=2024, month=12, day=25))
        # result = await session.execute(query)
        # result = result.scalars()
        p = Promotion(
            code="code15",
            sale=15,
            day_end=datetime.date.today(),
        )
        session.add(p)
        p.services = [PromotionToService(service_id=1), PromotionToService(service_id=2)]
        await session.flush()
        await session.commit()


if __name__ == "__main__":
    asyncio.new_event_loop().run_until_complete(add_promotion())
