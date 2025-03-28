from dishka import Provider, Scope, from_context, provide

from src.infrastructure.http_client.client import HTTPClientAdapter
from src.infrastructure.other_service_integration.schedule_service import ScheduleServiceIntegration
from src.presentation.api.settings import Settings


class OtherServiceProvider(Provider):
    scope = Scope.APP

    settings = from_context(provides=Settings)
    http_client = provide(HTTPClientAdapter)

    @provide()
    async def schedule_service_integration(
        self, settings: Settings, http_client: HTTPClientAdapter
    ) -> ScheduleServiceIntegration:
        return ScheduleServiceIntegration(settings=settings, client=http_client)
