from src.infrastructure.db.models.schedules import Master, Service, Schedule, Slot, Order
from src.logic.dto.mappers.user_mappers import user_to_detail_dto_mapper
from src.logic.dto.schedule_dto import MasterDetailDTO, ServiceDTO, ScheduleDetailDTO, ScheduleShortDTO, SlotShortDTO, \
    SlotDetailDTO, OrderDetailDTO


def master_to_detail_dto_mapper(master: Master) -> MasterDetailDTO:
    return MasterDetailDTO(
        id=master.id,
        user=user_to_detail_dto_mapper(master.user),
        description=master.description,
        services=[service_to_detail_dto_mapper(service) for service in master.services],
    )


def service_to_detail_dto_mapper(service: Service) -> ServiceDTO:
    return ServiceDTO(
        id=service.id,
        name=service.name,
        description=service.description,
        price=service.price,
    )


def schedule_to_detail_dto_mapper(schedule: Schedule) -> ScheduleDetailDTO:
    return ScheduleDetailDTO(id=schedule.id, day=schedule.day, master=master_to_detail_dto_mapper(schedule.master))


def schedule_to_short_dto_mapper(schedule: Schedule) -> ScheduleShortDTO:
    return ScheduleShortDTO(
        id=schedule.id,
        day=schedule.day,
    )


def slot_to_short_dto_mapper(slot: Slot) -> SlotShortDTO:
    return SlotShortDTO(
        id=slot.id,
        time_start=slot.time_start,
    )


def slot_to_detail_dto_mapper(slot: Slot) -> SlotDetailDTO:
    return SlotDetailDTO(id=slot.id, time_start=slot.time_start, schedule=schedule_to_detail_dto_mapper(slot.schedule))


def order_to_detail_dto_mapper(order: Order) -> OrderDetailDTO:
    return OrderDetailDTO(
        id=order.id,
        slot=slot_to_detail_dto_mapper(order.slot),
        service=service_to_detail_dto_mapper(order.service),
        user=user_to_detail_dto_mapper(order.user),
        date_add=order.date_add,
        photo_after_path=order.photo_after_path,
        photo_before_path=order.photo_before_path,
    )
