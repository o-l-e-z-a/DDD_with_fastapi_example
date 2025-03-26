from typing import Self

import aio_pika

from aio_pika.abc import AbstractRobustChannel, AbstractRobustConnection
from aiormq import AMQPConnectionError

from src.infrastructure.logger_adapter.logger import init_logger
from src.presentation.api.settings import Settings

logger = init_logger(__name__)


class RabbitConnector:
    def __init__(self, settings: Settings, loop: None = None):
        self._connection: AbstractRobustConnection | None = None
        self._channel: AbstractRobustChannel | None = None
        self.config = settings.rabbit
        self.loop = loop

    async def get_connection(self) -> AbstractRobustConnection | None:
        try:
            return await aio_pika.connect_robust(
                host=self.config.RABBIT_HOST,
                port=self.config.RABBIT_PORT,
                login=self.config.RABBIT_USER,
                password=self.config.RABBIT_PASS,
                loop=self.loop,
            )
        except AMQPConnectionError as err:
            logger.error(err)
            return None

    @property
    def channel(self) -> AbstractRobustChannel:
        if self._channel is None:
            raise Exception("Please use context manager for Rabbit helper.")
        return self._channel

    async def open_connection(self):
        self._connection = await self.get_connection()
        if self._connection:
            self._channel = await self._connection.channel()

    async def __aenter__(self) -> Self:
        await self.open_connection()
        return self

    async def __aexit__(self, *args, **kwargs) -> None:
        await self.close_connection()

    async def close_connection(self):
        if not self._channel.is_closed:
            await self._channel.close()
        if not self._connection.is_closed:
            await self._connection.close()
