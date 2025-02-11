from dishka import Provider, Scope, provide

from src.domain.orders.events import OrderCreatedEvent
from src.logic.commands.schedule_commands import (
    AddMasterCommand,
    AddMasterCommandHandler,
    AddOrderCommand,
    AddOrderCommandHandler,
    AddScheduleCommand,
    AddScheduleCommandHandler,
    CancelOrderCommand,
    CancelOrderCommandHandler,
    UpdateOrderCommand,
    UpdateOrderCommandHandler, StartOrderCommand, StartOrderCommandHandler, UpdatePhotoOrderCommand,
    UpdatePhotoOrderCommandHandler,
)
from src.logic.commands.user_commands import AddUserCommand, AddUserCommandHandler
from src.logic.events.order_handlers import OrderCreatedEmailEventHandler, OrderCreatedPointIncreaseEventHandler
from src.logic.mediator.base import Mediator
from src.logic.uows.order_uow import SQLAlchemyOrderUnitOfWork
from src.logic.uows.schedule_uow import SQLAlchemyScheduleUnitOfWork
from src.logic.uows.users_uow import SQLAlchemyUsersUnitOfWork


class LogicProvider(Provider):
    scope = Scope.APP

    user_uow = provide(SQLAlchemyUsersUnitOfWork)
    schedule_uow = provide(SQLAlchemyScheduleUnitOfWork)
    order_uow = provide(SQLAlchemyOrderUnitOfWork)

    @provide(scope=Scope.APP)
    def init_mediator(
        self,
        user_uow: SQLAlchemyUsersUnitOfWork,
        schedule_uow: SQLAlchemyScheduleUnitOfWork,
        order_uow: SQLAlchemyOrderUnitOfWork,
    ) -> Mediator:
        mediator = Mediator()
        mediator.register_command(AddUserCommand, [AddUserCommandHandler(mediator=mediator, uow=user_uow)])
        mediator.register_command(AddMasterCommand, [AddMasterCommandHandler(mediator=mediator, uow=schedule_uow)])
        mediator.register_command(AddScheduleCommand, [AddScheduleCommandHandler(mediator=mediator, uow=schedule_uow)])
        mediator.register_command(AddOrderCommand, [AddOrderCommandHandler(mediator=mediator, uow=schedule_uow)])
        mediator.register_command(UpdateOrderCommand, [UpdateOrderCommandHandler(mediator=mediator, uow=schedule_uow)])
        mediator.register_command(
            UpdatePhotoOrderCommand, [UpdatePhotoOrderCommandHandler(mediator=mediator, uow=schedule_uow)]
        )
        mediator.register_command(StartOrderCommand, [StartOrderCommandHandler(mediator=mediator, uow=schedule_uow)])
        mediator.register_command(CancelOrderCommand, [CancelOrderCommandHandler(mediator=mediator, uow=schedule_uow)])
        mediator.register_event(
            OrderCreatedEvent,
            [OrderCreatedPointIncreaseEventHandler(uow=schedule_uow), OrderCreatedEmailEventHandler(uow=schedule_uow)],
        )
        return mediator
