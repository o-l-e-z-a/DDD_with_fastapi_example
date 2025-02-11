import asyncio

from collections import defaultdict
from datetime import date, timedelta
from typing import Type

from dishka import make_async_container

from src.infrastructure.db.exceptions import InsertException
from src.infrastructure.db.provider import DBProvider
from src.logic.commands.schedule_commands import (
    AddMasterCommand,
    AddOrderCommand,
    AddScheduleCommand,
    CancelOrderCommand,
    UpdateOrderCommand,
)
from src.logic.commands.user_commands import AddUserCommand
from src.logic.mediator.base import Mediator
from src.logic.provider import LogicProvider
from src.presentation.api.schedules.schema import ScheduleSchema
from src.presentation.api.settings import Settings, settings


async def create_user():
    mediator = await container.get(Mediator)
    await mediator.handle_command(
        AddUserCommand(
            email="safas@wsefg.com",
            first_name="sad",
            last_name="asdas",
            telephone="880055534323",
            password="asdas@13H",
        )
    )


async def add_master():
    mediator = await container.get(Mediator)
    data = AddMasterCommand(
        description="asdasdasdasd",
        user_id=11,
        services_id=[1, 2],
    )
    await mediator.handle_command(data)


async def add_schedule():
    mediator = await container.get(Mediator)
    data = AddScheduleCommand(day=date.today() + timedelta(days=1), master_id=17)
    try:
        schedule, *_ = await mediator.handle_command(data)
    except InsertException as err:
        detail = err.title
        print(detail)
        return
    print(schedule)
    schedule_schema = ScheduleSchema.model_validate(schedule.to_dict())
    print(schedule_schema)


async def add_order():
    mediator = await container.get(Mediator)
    order_data = AddOrderCommand(
        slot_id=35,
        service_id=1,
        user_id=13,
    )
    await mediator.handle_command(order_data)


async def update_order():
    mediator = await container.get(Mediator)
    order_data = UpdateOrderCommand(
        slot_id=37,
        order_id=22,
        user_id=13,
    )
    await mediator.handle_command(order_data)


async def delete_order():
    mediator = await container.get(Mediator)
    user_id = 13
    order_data = CancelOrderCommand(user_id=user_id, order_id=19)
    await mediator.handle_command(order_data)


if __name__ == "__main__":
    container = make_async_container(LogicProvider(), DBProvider(), context={Settings: settings})
    asyncio.new_event_loop().run_until_complete(add_schedule())
