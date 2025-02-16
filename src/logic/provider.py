from dishka import Provider, Scope, provide

from src.domain.orders.events import OrderCreatedEvent
from src.infrastructure.db.uows.order_uow import SQLAlchemyOrderQueryUnitOfWork, SQLAlchemyOrderUnitOfWork
from src.infrastructure.db.uows.schedule_uow import SQLAlchemyScheduleQueryUnitOfWork, SQLAlchemyScheduleUnitOfWork
from src.infrastructure.db.uows.users_uow import SQLAlchemyUsersQueryUnitOfWork, SQLAlchemyUsersUnitOfWork
from src.logic.commands.schedule_commands import (
    AddMasterCommand,
    AddMasterCommandHandler,
    AddOrderCommand,
    AddOrderCommandHandler,
    AddScheduleCommand,
    AddScheduleCommandHandler,
    CancelOrderCommand,
    CancelOrderCommandHandler,
    StartOrderCommand,
    StartOrderCommandHandler,
    UpdateOrderCommand,
    UpdateOrderCommandHandler,
    UpdatePhotoOrderCommand,
    UpdatePhotoOrderCommandHandler,
)
from src.logic.commands.user_commands import AddUserCommand, AddUserCommandHandler
from src.logic.events.order_handlers import OrderCreatedEmailEventHandler, OrderCreatedPointIncreaseEventHandler
from src.logic.mediator.base import Mediator


class LogicProvider(Provider):
    scope = Scope.APP

    user_uow = provide(SQLAlchemyUsersUnitOfWork)
    schedule_uow = provide(SQLAlchemyScheduleUnitOfWork)
    order_uow = provide(SQLAlchemyOrderUnitOfWork)

    user_query_uow = provide(SQLAlchemyUsersQueryUnitOfWork)
    schedule_query_uow = provide(SQLAlchemyScheduleQueryUnitOfWork)
    order_query_uow = provide(SQLAlchemyOrderQueryUnitOfWork)

    @provide(scope=Scope.APP)
    def init_mediator(
        self,
        user_uow: SQLAlchemyUsersUnitOfWork,
        schedule_uow: SQLAlchemyScheduleUnitOfWork,
        order_uow: SQLAlchemyOrderUnitOfWork,
        user_query_uow: SQLAlchemyUsersQueryUnitOfWork,
        schedule_query_uow: SQLAlchemyScheduleQueryUnitOfWork,
        order_query_uow: SQLAlchemyOrderQueryUnitOfWork,
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
