from typing import Self

import aio_pika

from aio_pika.abc import AbstractRobustChannel, AbstractRobustConnection

from src.infrastructure.logger_adapter.logger import init_logger
from src.presentation.api.settings import Settings

logger = init_logger(__name__)


class RabbitConnector:
    def __init__(self, settings: Settings):
        self._connection: AbstractRobustConnection | None = None
        self._channel: AbstractRobustChannel | None = None
        self.config = settings.rabbit

    async def get_connection(self) -> AbstractRobustConnection:
        return await aio_pika.connect_robust(
            host=self.config.RABBIT_HOST,
            port=self.config.RABBIT_PORT,
            login=self.config.RABBIT_USER,
            password=self.config.RABBIT_PASS,
        )

    @property
    def channel(self) -> AbstractRobustChannel:
        if self._channel is None:
            raise Exception("Please use context manager for Rabbit helper.")
        return self._channel

    async def __aenter__(self) -> Self:
        self._connection = await self.get_connection()
        self._channel = await self._connection.channel()
        return self

    async def __aexit__(self, *args, **kwargs) -> None:
        if not self._channel.is_closed:
            await self._channel.close()
        if not self._connection.is_closed:
            await self._connection.close()
