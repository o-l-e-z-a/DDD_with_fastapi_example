import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import selectinload

from src.infrastructure.db.models.orders import Promotion, PromotionToService
from src.presentation.api.dependencies import setup_container


async def add_promotion():
    container = setup_container()
    session_factory = await container.get(async_sessionmaker)
    async with session_factory() as session:
        # query = select(Slot, Schedule).join(Schedule).filter_by(day=datetime.date(year=2024, month=12, day=25))
        # result = await session.execute(query)
        # result = result.scalars()
        query = select(Promotion).options(selectinload(Promotion.services)).filter_by(id=19)
        result = await session.execute(query)
        scalar = result.scalar_one_or_none()
        p = scalar.to_domain()
        model = Promotion.from_entity(p)
        p.services_id = [2, 1]
        services = [PromotionToService(service_id=service_id) for service_id in p.services_id]
        model.services = services
        await session.merge(model)
        await session.flush()
        await session.commit()


if __name__ == "__main__":
    asyncio.new_event_loop().run_until_complete(add_promotion())
