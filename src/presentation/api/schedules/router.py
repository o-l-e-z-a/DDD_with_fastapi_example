from dataclasses import asdict

from fastapi import APIRouter, status, Depends
from fastapi_cache.decorator import cache

from src.logic.services.schedule_service import ProcedureService, MasterService
from src.presentation.api.dependencies import get_procedure_service, get_master_service, get_schedule_service
from src.logic.dto.schedule_dto import InventoryAddDTO, InventoryUpdateDTO, MasterAddDTO, ScheduleAddDTO
from src.presentation.api.schedules.schema import ServiceSchema, InventorySchema, InventoryAddSchema, \
    InventoryUpdateSchema, MasterAddSchema, MasterReportSchema, MasterWithoutServiceSchema, MasterSchema
from src.presentation.api.users.schema import AllUserSchema

router = APIRouter(
    prefix='/api',
    tags=['schedule']
)


@router.get("/services/")
async def get_services(procedure_service: ProcedureService = Depends(get_procedure_service)):
    results = await procedure_service.get_services()
    service_schemas = [ServiceSchema.model_validate(service.to_dict()) for service in results]
    return service_schemas


@router.get("/inventories/", tags=['inventory'])
# @cache(expire=60)
async def get_inventories(procedure_service: ProcedureService = Depends(get_procedure_service)) -> list[InventorySchema]:
    results = await procedure_service.get_inventories()
    inventory_schemas = [InventorySchema.model_validate(inventory.to_dict()) for inventory in results]
    return inventory_schemas


@router.delete("/inventory/{inventory_id}/delete/", tags=['inventory'], status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory(inventory_id: int, procedure_service: ProcedureService = Depends(get_procedure_service)):
    await procedure_service.delete_inventory(inventory_id=inventory_id)


@router.patch("/inventory/{inventory_id}/update/", tags=['inventory'])
async def patch_inventory(
        inventory_id: int,
        inventory_data: InventoryUpdateSchema,
        procedure_service: ProcedureService = Depends(get_procedure_service)
) -> InventorySchema:
    print(f'inventory_data; {inventory_data}')
    inventory = await procedure_service.update_inventory(
         InventoryUpdateDTO(**inventory_data.model_dump(exclude_unset=True), inventory_id=inventory_id)
    )
    inventory_schema = InventorySchema.model_validate(inventory.to_dict())
    return inventory_schema


@router.post("/inventory/add/", tags=['inventory'], status_code=status.HTTP_201_CREATED)
async def add_inventory(
        inventory_data: InventoryAddSchema,
        procedure_service: ProcedureService = Depends(get_procedure_service)
) -> InventorySchema:
    inventory = await procedure_service.add_inventory(InventoryAddDTO(**inventory_data.model_dump()))
    inventory_schema = InventorySchema.model_validate(inventory.to_dict())
    return inventory_schema


@router.get("/all_masters/")
# @cache(expire=60)
async def get_all_masters(master_service: MasterService = Depends(get_master_service)) -> list[MasterSchema]:
    results = await master_service.get_all_masters()
    master_schemas = [MasterSchema.model_validate(master.to_dict()) for master in results]
    return master_schemas


@router.get("/all_user_to_add_masters/")
async def get_all_user_to_add_masters(master_service: MasterService = Depends(get_master_service)) -> list[AllUserSchema]:
    results = await master_service.get_all_user_to_add_masters()
    user_schemas = [AllUserSchema.model_validate(user.to_dict()) for user in results]
    return user_schemas


@router.post("/master/add/", status_code=status.HTTP_201_CREATED)
async def add_master(
        master_data: MasterAddSchema,
        master_service: MasterService = Depends(get_master_service)
) -> MasterSchema:
    services_ids = list(map(int, master_data.services.split(',')))
    master = await master_service.add_master(MasterAddDTO(
        description=master_data.description,
        user_id=master_data.user_id,
        services=services_ids
    ))
    master_schema = MasterSchema.model_validate(master.to_dict())
    return master_schema


@router.get("/service/{service_pk}/masters/", description='master_for_service')
async def get_masters_for_service(
        service_pk: int,
        master_service: MasterService = Depends(get_master_service)
) -> list[MasterWithoutServiceSchema]:
    results = await master_service.get_masters_for_service(service_int=service_pk)
    master_schemas = [MasterWithoutServiceSchema.model_validate(master.to_dict()) for master in results]
    return master_schemas


@router.get("/master_report/")
# @cache(expire=60)
async def get_master_report(master_service: MasterService = Depends(get_master_service)) -> list[MasterReportSchema]:
    results = await master_service.get_master_report()
    master_schemas = [MasterReportSchema.model_validate(master.to_dict()) for master in results]
    return master_schemas
