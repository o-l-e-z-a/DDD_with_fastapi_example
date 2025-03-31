from typing import Any

from src.logic.dto.order_dto import OrderShortDTO, ServiceDTO


def json_to_service_mapper(services: list[dict[str, Any]]) -> list[ServiceDTO]:
    return [
        ServiceDTO(
            id=service.get("id"),
            name=service.get("name"),
            description=service.get("description"),
            price=service.get("price"),
        )
        for service in services
    ]


def json_to_service_id_only_mapper(services: list[dict[str, Any]]) -> list[int]:
    return [service.get("id") for service in services]


def json_to_order_mapper(order: dict[str, Any]) -> OrderShortDTO:
    return OrderShortDTO(
        id=order.get("id"),
        date_add=order.get("date_add"),
        service_id=order.get("service").get("id"),
        user_id=order.get("user").get("id"),
        slot_id=order.get("slot").get("id"),
    )
