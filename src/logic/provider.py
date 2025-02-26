from dishka import Provider, Scope, provide

from src.infrastructure.broker.rabbit.consumer import RabbitConsumer
from src.infrastructure.broker.rabbit.producer import Producer
from src.infrastructure.db.uows.order_uow import SQLAlchemyOrderQueryUnitOfWork, SQLAlchemyOrderUnitOfWork
from src.infrastructure.db.uows.schedule_uow import SQLAlchemyScheduleQueryUnitOfWork, SQLAlchemyScheduleUnitOfWork
from src.infrastructure.db.uows.users_uow import SQLAlchemyUsersQueryUnitOfWork, SQLAlchemyUsersUnitOfWork
from src.logic.commands.order_commands import (
    AddPromotionCommand,
    AddPromotionCommandHandler,
    AdduserPointCommand,
    AdduserPointCommandHandler,
    DeletePromotionCommand,
    DeletePromotionCommandHandler,
    UpdatePromotionCommand,
    UpdatePromotionCommandHandler,
)
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
from src.logic.commands.user_commands import (
    AddUserCommand,
    AddUserCommandHandler,
    VerifyUserCredentialsCommand,
    VerifyUserCredentialsCommandHandler,
)
from src.logic.event_consumers.orders_consumers import UserCreatedEventConsumer
from src.logic.events.user_events import UserCreatedEvent, UserCreatedEventHandler
from src.logic.mediator.base import Mediator
from src.logic.queries.order_queries import (
    GetAllPromotionsQuery,
    GetAllPromotionsQueryHandler,
    UserPointQuery,
    UserPointQueryHandler,
)
from src.logic.queries.schedule_queries import (
    GetAllMasterQuery,
    GetAllMasterQueryHandler,
    GetAllOrdersQuery,
    GetAllOrdersQueryHandler,
    GetAllSchedulesQuery,
    GetAllSchedulesQueryHandler,
    GetAllServiceQuery,
    GetAllServiceQueryHandler,
    GetAllUsersToAddMasterQuery,
    GetAllUsersToAddMasterQueryHandler,
    GetMasterByUserQuery,
    GetMasterByUserQueryHandler,
    GetMasterForServiceQuery,
    GetMasterForServiceQueryHandler,
    GetMasterReportQuery,
    GetMasterReportQueryHandler,
    GetMasterScheduleQuery,
    GetMasterScheduleQueryHandler,
    GetScheduleSlotsQuery,
    GetScheduleSlotsQueryHandler,
    GetServiceForMasterQuery,
    GetServiceForMasterQueryHandler,
    GetServiceReportQuery,
    GetServiceReportQueryHandler,
    GetUserOrdersQuery,
    GetUserOrdersQueryHandler,
)
from src.logic.queries.user_queries import GetUserByIdQuery, GetUserByIdQueryHandler


class LogicProvider(Provider):
    scope = Scope.APP

    consumer = provide(RabbitConsumer)
    user_created_consumer = provide(UserCreatedEventConsumer)

    @provide(scope=Scope.APP)
    def init_mediator(
        self,
        user_uow: SQLAlchemyUsersUnitOfWork,
        schedule_uow: SQLAlchemyScheduleUnitOfWork,
        order_uow: SQLAlchemyOrderUnitOfWork,
        user_query_uow: SQLAlchemyUsersQueryUnitOfWork,
        schedule_query_uow: SQLAlchemyScheduleQueryUnitOfWork,
        order_query_uow: SQLAlchemyOrderQueryUnitOfWork,
        publisher: Producer,
        # connector: RabbitConnector,
    ) -> Mediator:
        mediator = Mediator()

        # commands
        mediator.register_command(AddUserCommand, [AddUserCommandHandler(mediator=mediator, uow=user_uow)])
        mediator.register_command(
            VerifyUserCredentialsCommand, [VerifyUserCredentialsCommandHandler(mediator=mediator, uow=user_uow)]
        )

        mediator.register_command(AddMasterCommand, [AddMasterCommandHandler(mediator=mediator, uow=schedule_uow)])
        mediator.register_command(AddScheduleCommand, [AddScheduleCommandHandler(mediator=mediator, uow=schedule_uow)])
        mediator.register_command(AddOrderCommand, [AddOrderCommandHandler(mediator=mediator, uow=schedule_uow)])
        mediator.register_command(UpdateOrderCommand, [UpdateOrderCommandHandler(mediator=mediator, uow=schedule_uow)])
        mediator.register_command(
            UpdatePhotoOrderCommand, [UpdatePhotoOrderCommandHandler(mediator=mediator, uow=schedule_uow)]
        )
        mediator.register_command(StartOrderCommand, [StartOrderCommandHandler(mediator=mediator, uow=schedule_uow)])
        mediator.register_command(CancelOrderCommand, [CancelOrderCommandHandler(mediator=mediator, uow=schedule_uow)])

        mediator.register_command(AddPromotionCommand, [AddPromotionCommandHandler(mediator=mediator, uow=order_uow)])
        mediator.register_command(
            UpdatePromotionCommand, [UpdatePromotionCommandHandler(mediator=mediator, uow=order_uow)]
        )
        mediator.register_command(
            DeletePromotionCommand, [DeletePromotionCommandHandler(mediator=mediator, uow=order_uow)]
        )
        mediator.register_command(AdduserPointCommand, [AdduserPointCommandHandler(mediator=mediator, uow=order_uow)])

        # query
        mediator.register_query(GetUserByIdQuery, GetUserByIdQueryHandler(uow=user_query_uow))

        mediator.register_query(GetAllServiceQuery, GetAllServiceQueryHandler(uow=schedule_query_uow))
        mediator.register_query(GetAllMasterQuery, GetAllMasterQueryHandler(uow=schedule_query_uow))
        mediator.register_query(GetAllSchedulesQuery, GetAllSchedulesQueryHandler(uow=schedule_query_uow))
        mediator.register_query(GetAllOrdersQuery, GetAllOrdersQueryHandler(uow=schedule_query_uow))
        mediator.register_query(GetAllUsersToAddMasterQuery, GetAllUsersToAddMasterQueryHandler(uow=schedule_query_uow))
        mediator.register_query(GetMasterScheduleQuery, GetMasterScheduleQueryHandler(uow=schedule_query_uow))
        mediator.register_query(GetMasterForServiceQuery, GetMasterForServiceQueryHandler(uow=schedule_query_uow))
        mediator.register_query(GetServiceForMasterQuery, GetServiceForMasterQueryHandler(uow=schedule_query_uow))
        mediator.register_query(GetScheduleSlotsQuery, GetScheduleSlotsQueryHandler(uow=schedule_query_uow))
        mediator.register_query(GetUserOrdersQuery, GetUserOrdersQueryHandler(uow=schedule_query_uow))
        mediator.register_query(GetMasterReportQuery, GetMasterReportQueryHandler(uow=schedule_query_uow))
        mediator.register_query(GetServiceReportQuery, GetServiceReportQueryHandler(uow=schedule_query_uow))
        mediator.register_query(GetMasterByUserQuery, GetMasterByUserQueryHandler(uow=schedule_query_uow))

        mediator.register_query(GetAllPromotionsQuery, GetAllPromotionsQueryHandler(uow=order_query_uow))
        mediator.register_query(UserPointQuery, UserPointQueryHandler(uow=order_query_uow))

        # events
        mediator.register_event(
            UserCreatedEvent,
            [UserCreatedEventHandler(uow=schedule_uow, message_broker=publisher)],
        )
        return mediator
