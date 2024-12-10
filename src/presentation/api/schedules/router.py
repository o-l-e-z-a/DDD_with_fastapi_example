from datetime import date

from fastapi import APIRouter, Depends, status
from fastapi_cache.decorator import cache

from src.logic.dto.schedule_dto import InventoryAddDTO, InventoryUpdateDTO, MasterAddDTO, ScheduleAddDTO
from src.logic.exceptions.base_exception import NotFoundLogicException
from src.logic.services.schedule_service import MasterService, ProcedureService, ScheduleService
from src.presentation.api.dependencies import (
    CurrentMaster,
    get_master_service,
    get_procedure_service,
    get_schedule_service,
)
from src.presentation.api.exceptions import NotFoundHTTPException
from src.presentation.api.schedules.schema import (
    InventoryAddSchema,
    InventorySchema,
    InventoryUpdateSchema,
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
)
from src.presentation.api.users.schema import AllUserSchema

router = APIRouter(prefix="/api", tags=["schedule"])


@router.get("/services/")
async def get_services(procedure_service: ProcedureService = Depends(get_procedure_service)):
    results = await procedure_service.get_services()
    service_schemas = [ServiceSchema.model_validate(service.to_dict()) for service in results]
    return service_schemas


@router.get("/inventories/", tags=["inventory"])
@cache(expire=60)
async def get_inventories(
    # admin: CurrentAdmin,
    procedure_service: ProcedureService = Depends(get_procedure_service),
) -> list[InventorySchema]:
    results = await procedure_service.get_inventories()
    inventory_schemas = [InventorySchema.model_validate(inventory.to_dict()) for inventory in results]
    return inventory_schemas


@router.delete("/inventory/{inventory_id}/delete/", tags=["inventory"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory(
    # admin: CurrentAdmin,
    inventory_id: int,
    procedure_service: ProcedureService = Depends(get_procedure_service),
):
    try:
        await procedure_service.delete_inventory(inventory_id=inventory_id)
    except NotFoundLogicException as err:
        raise NotFoundHTTPException(detail=err.title)


@router.patch("/inventory/{inventory_id}/update/", tags=["inventory"])
async def patch_inventory(
    # admin: CurrentAdmin,
    inventory_id: int,
    inventory_data: InventoryUpdateSchema,
    procedure_service: ProcedureService = Depends(get_procedure_service),
) -> InventorySchema:
    try:
        inventory = await procedure_service.update_inventory(
            InventoryUpdateDTO(**inventory_data.model_dump(exclude_unset=True), inventory_id=inventory_id)
        )
    except NotFoundLogicException as err:
        raise NotFoundHTTPException(detail=err.title)
    inventory_schema = InventorySchema.model_validate(inventory.to_dict())
    return inventory_schema


@router.post("/inventory/add/", tags=["inventory"], status_code=status.HTTP_201_CREATED)
async def add_inventory(
    # admin: CurrentAdmin,
    inventory_data: InventoryAddSchema,
    procedure_service: ProcedureService = Depends(get_procedure_service),
) -> InventorySchema:
    inventory = await procedure_service.add_inventory(InventoryAddDTO(**inventory_data.model_dump()))
    inventory_schema = InventorySchema.model_validate(inventory.to_dict())
    return inventory_schema


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
    all_day_slots = await schedule_service.get_slot_for_day(schedule_id=schedule_pk)
    return SlotsTimeSchema(slots=[slot_time.as_generic_type() for slot_time in all_day_slots])


@router.get("/master_schedule/{day}/", description="current_master_schedule")
async def get_current_master_schedule(
    day: date, master: CurrentMaster, schedule_service: ScheduleService = Depends(get_schedule_service)
) -> list[SlotSchema]:
    slots = await schedule_service.get_current_master_slots(day=day, master_id=master.id)
    slot_schemas = [SlotSchema.model_validate(slot.to_dict()) for slot in slots]
    return slot_schemas
