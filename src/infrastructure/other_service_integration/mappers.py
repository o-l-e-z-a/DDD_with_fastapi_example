from typing import Any

from src.logic.dto.schedule_dto import ServiceDTO


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
