from dataclasses import asdict
from datetime import date

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, UploadFile, status
from fastapi_cache.decorator import cache

from src.domain.schedules.exceptions import (
    SlotOccupiedException,
    OrderNotInProgressException,
    OrderNotReceivedException,
)
from src.infrastructure.db.exceptions import InsertException, UpdateException
from src.logic.exceptions.base_exception import NotFoundLogicException
from src.logic.exceptions.order_exceptions import NotUserOrderLogicException
from src.logic.mediator.base import Mediator
from src.logic.queries.schedule_queries import (
    GetAllServiceQuery,
    GetAllMasterQuery,
    GetAllUsersToAddMasterQuery,
    GetAllOrdersQuery,
    GetAllSchedulesQuery,
    GetMasterDaysQuery, GetMasterForServiceQuery, GetDaysForMasterAndServiceQuery
)
from src.logic.services.schedule_service import MasterService, ProcedureService, ScheduleService, OrderService
from src.presentation.api.dependencies import (
    CurrentMaster,
    CurrentUser,
    get_master_service,
    get_order_service,
    get_schedule_service,
)
from src.presentation.api.exceptions import (
    CannotUpdateDataToDatabase,
    NotCorrectDataHTTPException,
    NotFoundHTTPException,
    NotUserOrderException,
    OrderNotCorrectStatusException,
)
from src.presentation.api.schedules.schema import (
    MasterAddSchema,
    MasterDaysSchema,
    MasterReportSchema,
    MasterDetailSchema,
    MasterWithoutServiceSchema,
    ScheduleAddSchema,
    ScheduleSchema,
    ScheduleDetailSchema,
    ServiceSchema,
    SlotSchema,
    SlotsTimeSchema,
    OrderCreateSchema,
    OrderDetailSchema,
    AllOrderDetailSchema,
    OrderReportSchema,
    OrderUpdateSchema,
    MasterSchema,
    OrderSchema,
)
from src.logic.commands.schedule_commands import (
    AddMasterCommand,
    AddOrderCommand,
    AddScheduleCommand,
    CancelOrderCommand,
    UpdateOrderCommand,
    UpdatePhotoOrderCommand,
    StartOrderCommand,
    PhotoType,
)
from src.presentation.api.users.schema import AllUserSchema

router = APIRouter(route_class=DishkaRoute, prefix="/api", tags=["schedule"])


@router.get("/services/")
# @cache(expire=60)
async def get_services(
    mediator: FromDishka[Mediator],
):
    results = await mediator.handle_query(GetAllServiceQuery())
    service_schemas = [ServiceSchema.model_validate(service) for service in results]
    return service_schemas


@router.get("/all_masters/")
# @cache(expire=60)
async def get_all_masters(
    mediator: FromDishka[Mediator],
) -> list[MasterDetailSchema]:
    results = await mediator.handle_query(GetAllMasterQuery())
    master_schemas = [MasterDetailSchema.model_validate(master) for master in results]
    return master_schemas


@router.get("/all_user_to_add_masters/")
async def get_all_user_to_add_masters(
    # admin: CurrentAdmin,
    mediator: FromDishka[Mediator],
) -> list[AllUserSchema]:
    results = await mediator.handle_query(GetAllUsersToAddMasterQuery())
    user_schemas = [AllUserSchema.model_validate(user) for user in results]
    return user_schemas


@router.get("/schedules/")
# @cache(expire=60)
async def get_schedules(
    mediator: FromDishka[Mediator],
) -> list[ScheduleDetailSchema]:
    results = await mediator.handle_query(GetAllSchedulesQuery())
    schedule_schemas = [ScheduleDetailSchema.model_validate(schedule) for schedule in results]
    return schedule_schemas


@router.get("/all_orders/", description="все заказы для просмотра мастером")
# @cache(expire=60)
async def get_all_orders(
    mediator: FromDishka[Mediator],
) -> list[AllOrderDetailSchema]:
    results = await mediator.handle_query(GetAllOrdersQuery())
    order_schemas = [AllOrderDetailSchema.model_validate(order) for order in results]
    return order_schemas


@router.get("/master_days/")
# @cache(expire=60)
async def get_master_days(
    master: CurrentMaster,
    mediator: FromDishka[Mediator],
) -> MasterDaysSchema:
    results = await mediator.handle_query(GetMasterDaysQuery(master_id=master.id))
    return MasterDaysSchema(days=results)


@router.get("/service/{service_pk}/masters/", description="master_for_service")
async def get_masters_for_service(
    service_pk: int,
    mediator: FromDishka[Mediator],
) -> list[MasterWithoutServiceSchema]:
    results = await mediator.handle_query(GetMasterForServiceQuery(service_id=service_pk))
    master_schemas = [MasterWithoutServiceSchema.model_validate(master) for master in results]
    return master_schemas


@router.get("/master/{master_pk}/service/{service_pk}/schedules/", description="schedule days for service and master")
async def get_schedules_for_master_and_service(
    master_pk: int,
    service_pk: int,
    mediator: FromDishka[Mediator],
) -> MasterDaysSchema:
    results = await mediator.handle_query(GetDaysForMasterAndServiceQuery(master_id=master_pk, service_id=service_pk))
    return MasterDaysSchema(days=results)


@router.get("/slots/{schedule_pk}/", description="slot_for_day")
# @cache(expire=60)
async def get_slot_for_day(
    schedule_pk: int,
    schedule_service: ScheduleService = Depends(get_schedule_service)
) -> SlotsTimeSchema:
    try:
        all_day_slots = await schedule_service.get_slot_for_day(schedule_id=schedule_pk)
    except NotFoundLogicException as err:
        raise NotFoundHTTPException(detail=err.title)
    return SlotsTimeSchema(slots=[slot_time.as_generic_type() for slot_time in all_day_slots])


@router.get("/master_schedule/{day}/", description="current_master_schedule")
async def get_current_master_schedule(
    day: date,
    master: CurrentMaster,
    schedule_service: ScheduleService = Depends(get_schedule_service)
) -> list[SlotSchema]:
    slots = await schedule_service.get_current_master_slots(day=day, master_id=master.id)
    slot_schemas = [SlotSchema.model_validate(slot.to_dict()) for slot in slots]
    return slot_schemas


@router.get("/orders/", description="все заказы клиента")
# @cache(expire=60)
async def get_client_orders(
    user: CurrentUser,
    order_service: OrderService = Depends(get_order_service)
) -> list[OrderDetailSchema]:
    results = await order_service.get_client_orders(user=user)
    order_schemas = [OrderDetailSchema.model_validate(order.to_dict()) for order in results]
    return order_schemas


@router.get("/master_report/")
# @cache(expire=60)
async def get_master_report(
    # admin: CurrentAdmin,
    master_service: MasterService = Depends(get_master_service),
) -> list[MasterReportSchema]:
    results = await master_service.get_master_report()
    master_schemas = [MasterReportSchema.model_validate(master) for master in results]
    return master_schemas


@router.post("/service_report/")
async def get_service_report(
    # admin: CurrentAdmin,
    order_service: OrderService = Depends(get_order_service)
) -> list[OrderReportSchema]:
    report_results = await order_service.get_service_report()
    order_schema = [OrderReportSchema.model_validate(report) for report in report_results]
    return order_schema


@router.post("/schedule/add/", status_code=status.HTTP_201_CREATED)
async def add_schedule(
    schedule_data: ScheduleAddSchema,
    # admin: CurrentAdmin,
    mediator: FromDishka[Mediator],
) -> ScheduleSchema:
    try:
        schedule, *_ = await mediator.handle_command(AddScheduleCommand(**schedule_data.model_dump(exclude_unset=True)))
    except NotFoundLogicException as err:
        raise NotFoundHTTPException(detail=err.title)
    except InsertException as err:
        raise NotCorrectDataHTTPException(detail=err.title)
    schedule_schema = ScheduleSchema.model_validate(schedule.to_dict())
    return schedule_schema


@router.post("/order/add/", status_code=status.HTTP_201_CREATED)
async def add_order(
    order_data: OrderCreateSchema,
    user: CurrentUser,
    mediator: FromDishka[Mediator],
) -> OrderSchema:
    try:
        order, *_ = await mediator.handle_command(
            AddOrderCommand(
                slot_id=order_data.slot_id,
                service_id=order_data.service_id,
                user_id=user.id,
            ),
        )
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
    user: CurrentUser,
    mediator: FromDishka[Mediator],
) -> OrderSchema:
    try:
        order, *_ = await mediator.handle_command(
            UpdateOrderCommand(**slot_data.model_dump(), order_id=order_id, user_id=user.id),
        )
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
    master: CurrentMaster,
    mediator: FromDishka[Mediator],
) -> OrderSchema:
    try:
        order, *_ = await mediator.handle_command(
            StartOrderCommand(order_id=order_id),
        )
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
    master: CurrentMaster,
    mediator: FromDishka[Mediator],
) -> OrderSchema:
    photo_before_dto = PhotoType(
        file=photo_before.file, filename=photo_before.filename, content_type=photo_before.content_type
    )
    photo_after_dto = PhotoType(
        file=photo_after.file, filename=photo_after.filename, content_type=photo_after.content_type
    )
    try:
        order, *_ = await mediator.handle_command(
            UpdatePhotoOrderCommand(order_id=order_id, photo_before=photo_before_dto, photo_after=photo_after_dto)
        )
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
    user: CurrentUser,
    mediator: FromDishka[Mediator],
) -> OrderSchema:
    try:
        order, *_ = await mediator.handle_command(CancelOrderCommand(order_id=order_id, user_id=user.id))
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
    # admin: CurrentAdmin,
    mediator: FromDishka[Mediator],
) -> MasterSchema:
    services_ids = list(map(int, master_data.services.split(",")))
    try:
        master, *_ = await mediator.handle_command(
            AddMasterCommand(
                description=master_data.description, user_id=master_data.user_id, services_id=services_ids)
        )
    except NotFoundLogicException as err:
        raise NotFoundHTTPException(detail=err.title)
    except InsertException as err:
        raise NotCorrectDataHTTPException(detail=err.title)
    print(master.to_dict())
    master_schema = MasterSchema.model_validate(master.to_dict())
    return master_schema
