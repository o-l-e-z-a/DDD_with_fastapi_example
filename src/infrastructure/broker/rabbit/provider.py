from dishka import Provider, Scope, from_context, provide

from src.infrastructure.broker.rabbit.connector import RabbitConnector
from src.infrastructure.broker.rabbit.producer import Producer
from src.presentation.api.settings import Settings


class RabbitProvider(Provider):
    scope = Scope.APP

    settings = from_context(provides=Settings)

    connector = provide(RabbitConnector)
    publisher = provide(Producer)

    # @provide()
    # async def publisher(self, connector: RabbitConnector) -> Publisher:
    #     async with connector:
    #         return Publisher(connector.channel)
