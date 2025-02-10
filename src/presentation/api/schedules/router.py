from datetime import date

from fastapi import APIRouter, Depends, UploadFile, status
from fastapi_cache.decorator import cache

from src.domain.schedules.exceptions import SlotOccupiedException
from src.infrastructure.db.exceptions import InsertException, UpdateException
from src.logic.dto.order_dto import OrderCreateDTO, OrderUpdateDTO, PhotoDTO, TotalAmountDTO
from src.logic.dto.schedule_dto import MasterAddDTO, ScheduleAddDTO
from src.logic.exceptions.base_exception import NotFoundLogicException
from src.logic.exceptions.order_exceptions import NotUserOrderLogicException
from src.logic.services.order_service import OrderService
from src.logic.services.schedule_service import MasterService, ProcedureService, ScheduleService
from src.presentation.api.dependencies import (
    CurrentMaster,
    CurrentUser,
    get_master_service,
    get_order_service,
    get_procedure_service,
    get_schedule_service,
)
from src.presentation.api.exceptions import (
    CannotUpdateDataToDatabase,
    NotCorrectDataHTTPException,
    NotFoundHTTPException,
    NotUserOrderException,
)
from src.presentation.api.orders.schema import AllOrderSchema, OrderCreateSchema, OrderReportSchema, OrderSchema
from src.presentation.api.schedules.schema import (
    MasterAddSchema,
    MasterDaysSchema,
    MasterReportSchema,
    MasterSchema,
    MasterWithoutServiceSchema,
    ScheduleAddSchema,
    ScheduleSchema,
    ServiceSchema,
    SlotSchema,
    SlotsTimeSchema,
    SlotUpdateSchema,
)
from src.presentation.api.users.schema import AllUserSchema

router = APIRouter(prefix="/api", tags=["schedule"])


@router.get("/services/")
async def get_services(procedure_service: ProcedureService = Depends(get_procedure_service)):
    results = await procedure_service.get_services()
    service_schemas = [ServiceSchema.model_validate(service.to_dict()) for service in results]
    return service_schemas


@router.get("/all_masters/")
@cache(expire=60)
async def get_all_masters(master_service: MasterService = Depends(get_master_service)) -> list[MasterSchema]:
    results = await master_service.get_all_masters()
    master_schemas = [MasterSchema.model_validate(master.to_dict()) for master in results]
    return master_schemas


@router.get("/all_user_to_add_masters/")
async def get_all_user_to_add_masters(
    # admin: CurrentAdmin,
    master_service: MasterService = Depends(get_master_service),
) -> list[AllUserSchema]:
    results = await master_service.get_all_user_to_add_masters()
    user_schemas = [AllUserSchema.model_validate(user.to_dict()) for user in results]
    return user_schemas


@router.post("/master/add/", status_code=status.HTTP_201_CREATED)
async def add_master(
    # admin: CurrentAdmin,
    master_data: MasterAddSchema,
    master_service: MasterService = Depends(get_master_service),
) -> MasterSchema:
    services_ids = list(map(int, master_data.services.split(",")))
    try:
        master = await master_service.add_master(
            MasterAddDTO(description=master_data.description, user_id=master_data.user_id, services_id=services_ids)
        )
    except NotFoundLogicException as err:
        raise NotFoundHTTPException(detail=err.title)
    master_schema = MasterSchema.model_validate(master.to_dict())
    return master_schema


@router.get("/service/{service_pk}/masters/", description="master_for_service")
async def get_masters_for_service(
    service_pk: int, master_service: MasterService = Depends(get_master_service)
) -> list[MasterWithoutServiceSchema]:
    results = await master_service.get_masters_for_service(service_int=service_pk)
    master_schemas = [MasterWithoutServiceSchema.model_validate(master.to_dict()) for master in results]
    return master_schemas


@router.get("/master_report/")
@cache(expire=60)
async def get_master_report(
    # admin: CurrentAdmin,
    master_service: MasterService = Depends(get_master_service),
) -> list[MasterReportSchema]:
    results = await master_service.get_master_report()
    master_schemas = [MasterReportSchema.model_validate(master) for master in results]
    return master_schemas


@router.get("/schedules/")
@cache(expire=60)
async def get_schedules(schedule_service: ScheduleService = Depends(get_schedule_service)) -> list[ScheduleSchema]:
    results = await schedule_service.get_schedules()
    schedule_schemas = [ScheduleSchema.model_validate(schedule.to_dict()) for schedule in results]
    return schedule_schemas


@router.post("/schedule/add/", status_code=status.HTTP_201_CREATED)
async def add_schedule(
    # admin: CurrentAdmin,
    schedule_data: ScheduleAddSchema,
    schedule_service: ScheduleService = Depends(get_schedule_service),
) -> ScheduleSchema:
    try:
        schedule = await schedule_service.add_schedule(ScheduleAddDTO(**schedule_data.model_dump(exclude_unset=True)))
    except NotFoundLogicException as err:
        raise NotFoundHTTPException(detail=err.title)
    except InsertException as err:
        raise NotCorrectDataHTTPException(detail=err.title)
    schedule_schema = ScheduleSchema.model_validate(schedule.to_dict())
    return schedule_schema


@router.get("/master_days/")
@cache(expire=60)
async def get_master_days(
    master: CurrentMaster, schedule_service: ScheduleService = Depends(get_schedule_service)
) -> MasterDaysSchema:
    days = await schedule_service.get_master_days(master_id=master.id)
    return MasterDaysSchema(days=days)


@router.get("/master/{master_pk}/service/{service_pk}/schedules/", description="day_for_master")
async def get_day_for_master(
    master_pk: int, service_pk: int, schedule_service: ScheduleService = Depends(get_schedule_service)
) -> MasterDaysSchema:
    days = await schedule_service.get_day_for_master(master_id=master_pk, service_id=service_pk)
    return MasterDaysSchema(days=days)


@router.get("/slots/{schedule_pk}/", description="slot_for_day")
@cache(expire=60)
async def get_slot_for_day(
    schedule_pk: int, schedule_service: ScheduleService = Depends(get_schedule_service)
) -> SlotsTimeSchema:
    try:
        all_day_slots = await schedule_service.get_slot_for_day(schedule_id=schedule_pk)
    except NotFoundLogicException as err:
        raise NotFoundHTTPException(detail=err.title)
    return SlotsTimeSchema(slots=[slot_time.as_generic_type() for slot_time in all_day_slots])


@router.get("/master_schedule/{day}/", description="current_master_schedule")
async def get_current_master_schedule(
    day: date, master: CurrentMaster, schedule_service: ScheduleService = Depends(get_schedule_service)
) -> list[SlotSchema]:
    slots = await schedule_service.get_current_master_slots(day=day, master_id=master.id)
    slot_schemas = [SlotSchema.model_validate(slot.to_dict()) for slot in slots]
    return slot_schemas


@router.get("/all_orders/", description="все заказы для просмотра мастером")
@cache(expire=60)
async def get_all_orders(order_service: OrderService = Depends(get_order_service)) -> list[AllOrderSchema]:
    results = await order_service.get_all_orders()
    order_schemas = [AllOrderSchema.model_validate(order.to_dict()) for order in results]
    return order_schemas


@router.get("/orders/", description="все заказы клиента")
@cache(expire=60)
async def get_client_orders(
    user: CurrentUser, order_service: OrderService = Depends(get_order_service)
) -> list[OrderSchema]:
    results = await order_service.get_client_orders(user=user)
    order_schemas = [OrderSchema.model_validate(order.to_dict()) for order in results]
    return order_schemas


@router.post("/order/add/", status_code=status.HTTP_201_CREATED)
async def add_order(
    order_data: OrderCreateSchema,
    user: CurrentUser,
    order_service: OrderService = Depends(get_order_service),
) -> OrderSchema:
    try:
        order = await order_service.add_order(
            order_data=OrderCreateDTO(
                total_amount=TotalAmountDTO(
                    schedule_id=order_data.slot.schedule_id,
                    point=order_data.point,
                    promotion_code=order_data.promotion_code,
                ),
                time_start=order_data.slot.time_start,
            ),
            user=user,
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
    slot_data: SlotUpdateSchema,
    user: CurrentUser,
    order_service: OrderService = Depends(get_order_service),
) -> OrderSchema:
    try:
        order = await order_service.update_order(
            order_data=OrderUpdateDTO(**slot_data.model_dump(), order_id=order_id), user=user
        )
    except NotFoundLogicException as err:
        raise NotFoundHTTPException(detail=err.title)
    except NotUserOrderLogicException as err:
        raise NotUserOrderException(detail=err.title)
    except SlotOccupiedException as err:
        raise NotCorrectDataHTTPException(detail=err.title)
    order_schema = OrderSchema.model_validate(order.to_dict())
    return order_schema


@router.patch("/order/{order_id}/update_photo/")
async def update_photo(
    order_id: int,
    photo_before: UploadFile,
    photo_after: UploadFile,
    order_service: OrderService = Depends(get_order_service),
) -> OrderSchema:
    photo_before_dto = PhotoDTO(
        file=photo_before.file, filename=photo_before.filename, content_type=photo_before.content_type
    )
    photo_after_dto = PhotoDTO(
        file=photo_after.file, filename=photo_after.filename, content_type=photo_after.content_type
    )
    try:
        order = await order_service.update_order_photos(
            order_id=order_id, photo_before=photo_before_dto, photo_after=photo_after_dto
        )
    except NotFoundLogicException as err:
        raise NotFoundHTTPException(detail=err.title)
    except NotUserOrderLogicException as err:
        raise NotUserOrderException(detail=err.title)
    except UpdateException as err:
        raise CannotUpdateDataToDatabase(detail=err.title)
    order_schema = OrderSchema.model_validate(order.to_dict())
    return order_schema


@router.delete("/order/{order_id}/cancel/", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_order(
    order_id: int,
    user: CurrentUser,
    order_service: OrderService = Depends(get_order_service),
):
    try:
        await order_service.delete_order(order_id=order_id, user=user)
    except NotFoundLogicException as err:
        raise NotFoundHTTPException(detail=err.title)
    except NotUserOrderLogicException as err:
        raise NotUserOrderException(detail=err.title)


@router.post("/service_report/")
async def get_service_report(order_service: OrderService = Depends(get_order_service)) -> list[OrderReportSchema]:
    report_results = await order_service.get_service_report()
    order_schema = [OrderReportSchema.model_validate(report) for report in report_results]
    return order_schema
