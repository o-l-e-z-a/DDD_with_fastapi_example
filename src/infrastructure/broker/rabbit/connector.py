from typing import Any, Self

import aio_pika

from aio_pika.abc import AbstractRobustChannel, AbstractRobustConnection
from aiormq import AMQPConnectionError

from src.infrastructure.logger_adapter.logger import init_logger
from src.presentation.api.settings import Settings

logger = init_logger(__name__)


class BlankChannelException(Exception):
    message = "Please use context manager for Rabbit helper or check connection"


def except_rabbit_exception_deco(func):
    async def wrapped(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except BlankChannelException as err:
            logger.error(f"err: {err}")
            return None

    return wrapped


class RabbitConnector:
    def __init__(self, settings: Settings):
        self._connection: AbstractRobustConnection | None = None
        self._channel: AbstractRobustChannel | None = None
        self.config = settings.rabbit

    async def get_connection(self) -> AbstractRobustConnection | None:
        try:
            return await aio_pika.connect_robust(
                host=self.config.RABBIT_HOST,
                port=self.config.RABBIT_PORT,
                login=self.config.RABBIT_USER,
                password=self.config.RABBIT_PASS,
            )
        except AMQPConnectionError as err:
            logger.error(err)
            return None

    @property
    def channel(self) -> AbstractRobustChannel:
        if self._channel is None:
            raise BlankChannelException()
        return self._channel

    async def open_connection(self):
        self._connection = await self.get_connection()
        if self._connection:
            self._channel = await self._connection.channel()
            await self._channel.set_qos(prefetch_count=1)

    async def __aenter__(self) -> Self:
        await self.open_connection()
        return self

    async def __aexit__(self, *args, **kwargs) -> None:
        await self.close_connection()

    async def close_connection(self):
        if self._channel and not self._channel.is_closed:
            await self._channel.close()
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
