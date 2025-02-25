from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, UploadFile, status

from src.domain.schedules.entities import Master, Order, Schedule
from src.domain.schedules.exceptions import (
    OrderNotInProgressException,
    OrderNotReceivedException,
    SlotOccupiedException,
)
from src.infrastructure.db.exceptions import InsertException, UpdateException
from src.logic.commands.schedule_commands import (
    AddMasterCommand,
    AddOrderCommand,
    AddScheduleCommand,
    CancelOrderCommand,
    PhotoType,
    StartOrderCommand,
    UpdateOrderCommand,
    UpdatePhotoOrderCommand,
)
from src.logic.dto.schedule_dto import (
    MasterDetailDTO,
    MasterReportDTO,
    OrderDetailDTO,
    ScheduleDetailDTO,
    ScheduleShortDTO,
    ServiceDTO,
    ServiceReportDTO,
    SlotShortDTO,
)
from src.logic.dto.user_dto import UserDetailDTO
from src.logic.exceptions.base_exception import NotFoundLogicException
from src.logic.exceptions.order_exceptions import NotUserOrderLogicException
from src.logic.mediator.base import Mediator
from src.logic.queries.schedule_queries import (
    GetAllMasterQuery,
    GetAllOrdersQuery,
    GetAllSchedulesQuery,
    GetAllServiceQuery,
    GetAllUsersToAddMasterQuery,
    GetMasterForServiceQuery,
    GetMasterReportQuery,
    GetMasterScheduleQuery,
    GetScheduleSlotsQuery,
    GetServiceForMasterQuery,
    GetServiceReportQuery,
    GetUserOrdersQuery,
)
from src.presentation.api.dependencies import CurrentMaster, CurrentUser
from src.presentation.api.exceptions import (
    CannotUpdateDataToDatabase,
    NotCorrectDataHTTPException,
    NotFoundHTTPException,
    NotUserOrderException,
    OrderNotCorrectStatusException,
)
from src.presentation.api.schedules.schema import (
    AllOrderDetailSchema,
    MasterAddSchema,
    MasterDetailSchema,
    MasterReportSchema,
    MasterSchema,
    MasterWithoutServiceSchema,
    OrderCreateSchema,
    OrderDetailSchema,
    OrderReportSchema,
    OrderSchema,
    OrderUpdateSchema,
    ScheduleAddSchema,
    ScheduleDay,
    ScheduleDetailSchema,
    ScheduleSchema,
    ServiceSchema,
    SlotTimeSchema,
)
from src.presentation.api.users.schema import AllUserSchema

router = APIRouter(route_class=DishkaRoute, prefix="/api", tags=["schedule"])


@router.get("/services/")
# @cache(expire=60)
async def get_services(
    mediator: FromDishka[Mediator],
):
    results: list[ServiceDTO] = await mediator.handle_query(GetAllServiceQuery())
    service_schemas = [ServiceSchema.model_validate(result) for result in results]
    return service_schemas


@router.get("/all_masters/")
# @cache(expire=60)
async def get_all_masters(
    mediator: FromDishka[Mediator],
) -> list[MasterDetailSchema]:
    results: list[MasterDetailDTO] = await mediator.handle_query(GetAllMasterQuery())
    master_schemas = [MasterDetailSchema.model_validate(result) for result in results]
    return master_schemas


@router.get("/all_user_to_add_masters/")
async def get_all_user_to_add_masters(
    # admin: FromDishka[CurrentAdmin],
    mediator: FromDishka[Mediator],
) -> list[AllUserSchema]:
    results: list[UserDetailDTO] = await mediator.handle_query(GetAllUsersToAddMasterQuery())
    user_schemas = [AllUserSchema.model_validate(result) for result in results]
    return user_schemas


@router.get("/schedules/")
# @cache(expire=60)
async def get_schedules(
    mediator: FromDishka[Mediator],
) -> list[ScheduleDetailSchema]:
    results: list[ScheduleDetailDTO] = await mediator.handle_query(GetAllSchedulesQuery())
    schedule_schemas = [ScheduleDetailSchema.model_validate(result) for result in results]
    return schedule_schemas


@router.get("/all_orders/", description="все заказы для просмотра мастером")
# @cache(expire=60)
async def get_all_orders(
    mediator: FromDishka[Mediator],
) -> list[AllOrderDetailSchema]:
    results: list[OrderDetailDTO] = await mediator.handle_query(GetAllOrdersQuery())
    order_schemas = [AllOrderDetailSchema.model_validate(result) for result in results]
    return order_schemas


@router.get("/master_schedules/")
# @cache(expire=60)
async def get_master_schedules(
    master: FromDishka[CurrentMaster],
    mediator: FromDishka[Mediator],
) -> list[ScheduleDay]:
    results: list[ScheduleShortDTO] = await mediator.handle_query(GetMasterScheduleQuery(master_id=master.id))
    schedule_schemas = [ScheduleDay.model_validate(result) for result in results]
    return schedule_schemas


@router.get("/service/{service_pk}/masters/", description="master_for_service")
async def get_masters_for_service(
    service_pk: int,
    mediator: FromDishka[Mediator],
) -> list[MasterWithoutServiceSchema]:
    results: list[MasterDetailDTO] = await mediator.handle_query(GetMasterForServiceQuery(service_id=service_pk))
    master_schemas = [MasterWithoutServiceSchema.model_validate(result) for result in results]
    return master_schemas


@router.get("/masters/{master_pk}/services", description="service_for_master")
async def get_service_for_masters(
    master_pk: int,
    mediator: FromDishka[Mediator],
) -> list[ServiceSchema]:
    results: list[ServiceDTO] = await mediator.handle_query(GetServiceForMasterQuery(master_id=master_pk))
    service_schemas = [ServiceSchema.model_validate(result) for result in results]
    return service_schemas


@router.get("/master/{master_pk}/schedules/", description="schedule days for service and master")
async def get_schedules_for_master(
    master_pk: int,
    mediator: FromDishka[Mediator],
) -> list[ScheduleDay]:
    results: list[ScheduleShortDTO] = await mediator.handle_query(GetMasterScheduleQuery(master_id=master_pk))
    schedule_schemas = [ScheduleDay.model_validate(result) for result in results]
    return schedule_schemas


@router.get("/slots/{schedule_pk}/", description="Все свободное время на день")
# @cache(expire=60)
async def get_slot_for_day(
    schedule_pk: int,
    mediator: FromDishka[Mediator],
) -> list[SlotTimeSchema]:
    results: list[SlotShortDTO] = await mediator.handle_query(GetScheduleSlotsQuery(schedule_id=schedule_pk))
    slot_schemas = [SlotTimeSchema.model_validate(result) for result in results]
    return slot_schemas


@router.get("/orders/", description="все заказы клиента")
# @cache(expire=60)
async def get_client_orders(
    user: FromDishka[CurrentUser],
    mediator: FromDishka[Mediator],
) -> list[OrderDetailSchema]:
    results: list[OrderDetailDTO] = await mediator.handle_query(GetUserOrdersQuery(user_id=user.id))
    order_schemas = [OrderDetailSchema.model_validate(result) for result in results]
    return order_schemas


@router.get("/master_report/")
# @cache(expire=60)
async def get_master_report(
    # admin: FromDishka[CurrentAdmin],
    mediator: FromDishka[Mediator],
) -> list[MasterReportSchema]:
    results: list[MasterReportDTO] = await mediator.handle_query(GetMasterReportQuery())
    master_schemas = [MasterReportSchema.model_validate(result) for result in results]
    return master_schemas


@router.get("/service_report/")
# @cache(expire=60)
async def get_service_report(
    # admin: FromDishka[CurrentAdmin],
    mediator: FromDishka[Mediator],
) -> list[OrderReportSchema]:
    results: list[ServiceReportDTO] = await mediator.handle_query(GetServiceReportQuery())
    order_schema = [OrderReportSchema.model_validate(result) for result in results]
    return order_schema


@router.post("/schedule/add/", status_code=status.HTTP_201_CREATED)
async def add_schedule(
    schedule_data: ScheduleAddSchema,
    # admin: FromDishka[CurrentAdmin],
    mediator: FromDishka[Mediator],
) -> ScheduleSchema:
    try:
        schedule: Schedule = (
            await mediator.handle_command(AddScheduleCommand(**schedule_data.model_dump(exclude_unset=True)))
        )[0]
    except NotFoundLogicException as err:
        raise NotFoundHTTPException(detail=err.title)
    except InsertException as err:
        raise NotCorrectDataHTTPException(detail=err.title)
    schedule_schema = ScheduleSchema.model_validate(schedule.to_dict())
    return schedule_schema


@router.post("/order/add/", status_code=status.HTTP_201_CREATED)
async def add_order(
    order_data: OrderCreateSchema,
    user: FromDishka[CurrentUser],
    mediator: FromDishka[Mediator],
) -> OrderSchema:
    try:
        order: Order = (
            await mediator.handle_command(
                AddOrderCommand(
                    slot_id=order_data.slot_id,
                    service_id=order_data.service_id,
                    user_id=user.id,
                ),
            )
        )[0]
    except NotFoundLogicException as err:
        raise NotFoundHTTPException(detail=err.title)
    except SlotOccupiedException as err:
        raise NotCorrectDataHTTPException(detail=err.title)
    order_schema = OrderSchema.model_validate(order.to_dict())
    # order_create_send_mail_task.delay(order_dict)
    return order_schema


@router.put("/order/{order_id}/update/")
async def update_order(
    order_id: int,
    slot_data: OrderUpdateSchema,
    user: FromDishka[CurrentUser],
    mediator: FromDishka[Mediator],
) -> OrderSchema:
    try:
        order: Order = (
            await mediator.handle_command(
                UpdateOrderCommand(**slot_data.model_dump(), order_id=order_id, user_id=user.id),
            )
        )[0]
    except NotFoundLogicException as err:
        raise NotFoundHTTPException(detail=err.title)
    except NotUserOrderLogicException as err:
        raise NotUserOrderException(detail=err.title)
    except OrderNotReceivedException as err:
        raise OrderNotCorrectStatusException(detail=err.title)
    except SlotOccupiedException as err:
        raise NotCorrectDataHTTPException(detail=err.title)
    order_schema = OrderSchema.model_validate(order.to_dict())
    return order_schema


@router.put("/order/{order_id}/start/")
async def start_order(
    order_id: int,
    master: FromDishka[CurrentMaster],
    mediator: FromDishka[Mediator],
) -> OrderSchema:
    try:
        order: Order = (
            await mediator.handle_command(
                StartOrderCommand(order_id=order_id),
            )
        )[0]
    except NotFoundLogicException as err:
        raise NotFoundHTTPException(detail=err.title)
    except OrderNotReceivedException as err:
        raise OrderNotCorrectStatusException(detail=err.title)
    except SlotOccupiedException as err:
        raise NotCorrectDataHTTPException(detail=err.title)
    order_schema = OrderSchema.model_validate(order.to_dict())
    return order_schema


@router.patch("/order/{order_id}/update_photo/")
async def update_photo(
    order_id: int,
    photo_before: UploadFile,
    photo_after: UploadFile,
    master: FromDishka[CurrentMaster],
    mediator: FromDishka[Mediator],
) -> OrderSchema:
    photo_before_dto = PhotoType(
        file=photo_before.file, filename=photo_before.filename, content_type=photo_before.content_type
    )
    photo_after_dto = PhotoType(
        file=photo_after.file, filename=photo_after.filename, content_type=photo_after.content_type
    )
    try:
        order: Order = (
            await mediator.handle_command(
                UpdatePhotoOrderCommand(order_id=order_id, photo_before=photo_before_dto, photo_after=photo_after_dto)
            )
        )[0]
    except NotFoundLogicException as err:
        raise NotFoundHTTPException(detail=err.title)
    except OrderNotInProgressException as err:
        raise NotUserOrderException(detail=err.title)
    except UpdateException as err:
        raise CannotUpdateDataToDatabase(detail=err.title)
    print(order.to_dict())
    order_schema = OrderSchema.model_validate(order.to_dict())
    return order_schema


@router.patch("/order/{order_id}/cancel/")
async def cancel_order(
    order_id: int,
    user: FromDishka[CurrentUser],
    mediator: FromDishka[Mediator],
) -> OrderSchema:
    try:
        order: Order = (await mediator.handle_command(CancelOrderCommand(order_id=order_id, user_id=user.id)))[0]
    except NotFoundLogicException as err:
        raise NotFoundHTTPException(detail=err.title)
    except OrderNotReceivedException as err:
        raise OrderNotCorrectStatusException(detail=err.title)
    except NotUserOrderLogicException as err:
        raise NotUserOrderException(detail=err.title)
    order_schema = OrderSchema.model_validate(order.to_dict())
    return order_schema


@router.post("/master/add/", status_code=status.HTTP_201_CREATED)
async def add_master(
    master_data: MasterAddSchema,
    # admin: FromDishka[CurrentAdmin],
    mediator: FromDishka[Mediator],
) -> MasterSchema:
    services_ids = list(map(int, master_data.services.split(",")))
    try:
        master: Master = (
            await mediator.handle_command(
                AddMasterCommand(
                    description=master_data.description, user_id=master_data.user_id, services_id=services_ids
                )
            )
        )[0]
    except NotFoundLogicException as err:
        raise NotFoundHTTPException(detail=err.title)
    except InsertException as err:
        raise NotCorrectDataHTTPException(detail=err.title)
    print(master.to_dict())
    master_schema = MasterSchema.model_validate(master.to_dict())
    return master_schema
