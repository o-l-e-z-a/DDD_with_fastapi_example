from src.infrastructure.http_client.client import HTTPClientAdapter, HTTPMethod, HTTPParams
from src.infrastructure.other_service_integration.base import BaseServiceIntegration, ServiceNotAvailableError
from src.infrastructure.other_service_integration.mappers import json_to_order_mapper, json_to_service_id_only_mapper
from src.presentation.api.settings import Settings


class ScheduleServiceIntegration(BaseServiceIntegration):
    def __init__(self, client: HTTPClientAdapter, settings: Settings):
        base_url = (
            f"{settings.other_service_config.SCHEDULE_SERVICE_HOST}:"
            f"{settings.other_service_config.SCHEDULE_SERVICE_PORT}"
        )
        super().__init__(client=client, base_url=base_url)

    async def get_services_id_only(self, schedules_id: list[int]) -> list[int] | None:
        param = HTTPParams(
            url="http://127.0.0.1:8000/api/services/", query_params={"services_id": schedules_id}, method=HTTPMethod.GET
        )
        try:
            result = await self.client.get(param)
            return json_to_service_id_only_mapper(result)
        except ServiceNotAvailableError:
            return None

    async def get_order_by_id(self, order_id: int):
        param = HTTPParams(url=f"http://127.0.0.1:8000/api/order/{order_id}", method=HTTPMethod.GET)
        try:
            result = await self.client.get(param)
            return json_to_order_mapper(result)
        except ServiceNotAvailableError:
            return None
