import asyncio
import os
import sys

from pprint import pprint

from src.domain.base.values import CountNumber, Name
from src.domain.users.entities import User
from src.domain.users.values import Email, HumanName, Telephone
from src.infrastructure.db.repositories.users import UserRepository
from src.infrastructure.db.uows.schedule_uow import SQLAlchemyScheduleUnitOfWork

sys.path.insert(1, os.path.join(sys.path[0], ".."))


async def tesing():
    async with AsyncSessionFactory() as session:
        repo = UserRepository(session)
        # new_user_id = 4
        new_user = User(
            email=Email("ivanov2@mail.ru"),
            first_name=HumanName("Ivan"),
            last_name=HumanName("Ivanov"),
            telephone=Telephone("880005553536"),
        )
        new_user.hashed_password = "asdasdasd"
        print(f"new_user: {new_user}")
        new_user_after_repo = await repo.add(new_user)
        print(f"new_user_after_repo: {new_user_after_repo}")
        print(f"new_user: {new_user}")
        await session.flush()
        print(f"new_user_after_repo after flush: {new_user_after_repo}")
        print(f"new_user after flush: {new_user}")
        await session.commit()
        print(f"new_user_after_repo after commit: {new_user_after_repo}")
        print(f"new_user after commit: {new_user}")
        # new_user = await repo.find_one_or_none(id=new_user_id)
        # print(new_user)
        # new_domain_user = new_user.to_domain()
        # print(new_domain_user)


async def user_point_fdsa():
    async with AsyncSessionFactory() as session:
        repo = UserPointRepository(session)
        new_user_id = 4
        new_user_point_id = 1
        # new_user_point_id = await repo.add(
        #     user_id=4
        # )
        print(new_user_point_id)
        await session.commit()
        new_user_point = await repo.find_one_or_none(id=new_user_point_id)
        print("new_user_point ", new_user_point)
        if new_user_point:
            new_domain_new_user_point = new_user_point.to_domain()
            print(new_domain_new_user_point.user)
            print("new_domain_new_user_point ", new_domain_new_user_point)


async def update():
    async with AsyncSessionFactory() as session:
        repo = UserRepository(session)
        new_user_id = 4
        old_user = await repo.find_one_or_none(id=new_user_id)
        old_user_domain = old_user.to_domain()
        print(old_user_domain.first_name)
        old_user_domain.first_name = HumanName("asdasdasd")

        await repo.update(old_user_domain)

        new_user = await repo.find_one_or_none(id=new_user_id)
        print(new_user.first_name)
        new_user_domain = new_user.to_domain()
        print(new_user_domain)
        await session.commit()


async def add_inventory():
    async with AsyncSessionFactory() as session:
        repo = InventoryRepository(session)
        # new_user_id = 4
        new_user = Inventory(name=Name("shampoo"), unit=Name("ml"), stock_count=CountNumber(1000))
        print(f"new_user: {new_user}")
        new_user_after_repo = await repo.add(new_user)
        print(f"new_user_after_repo: {new_user_after_repo}")
        await session.flush()
        print(f"new_user_after_repo after flush: {new_user_after_repo}")
        await session.commit()
        print(f"new_user_after_repo after commit: {new_user_after_repo}")
        pprint(await repo.find_all())


async def update_inventory():
    async with AsyncSessionFactory() as session:
        repo = InventoryRepository(session)
        new_user = Inventory(name=Name("shampoo13"), unit=Name("ml"), stock_count=CountNumber(10300))
        print(f"new_user: {new_user}")
        new_user_after_repo = await repo.add(new_user)
        print(f"new_user_after_repo: {new_user_after_repo}")
        await session.flush()
        print(f"new_user_after_repo after flush: {new_user_after_repo}")
        pprint(await repo.find_all())
        print(f"new_user_after_repo after commit: {new_user_after_repo}")
        new_user_after_repo.stock_count = CountNumber(13)
        await repo.update(new_user_after_repo)
        pprint(await repo.find_all())
        await session.commit()


async def get_service():
    uow = SQLAlchemyScheduleUnitOfWork()
    async with uow:
        # async
        services = await uow.services.get_services_by_ids([1])
        services = await uow.services.find_all()
        print(services)


if __name__ == "__main__":
    asyncio.run(get_service())
    # asyncio.run(update())
