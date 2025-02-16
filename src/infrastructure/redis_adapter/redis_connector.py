from typing import Literal

import redis.exceptions

from redis import Redis
from redis.asyncio import Redis as AsyncRedis

from src.infrastructure.logger_adapter.logger import init_logger
from src.presentation.api.settings import settings

logger = init_logger(__name__)


class RedisConnector:
    def __init__(
        self,
        host: str = settings.redis.REDIS_HOST,
        port: int = settings.redis.REDIS_PORT,
        db: int = settings.redis.REDIS_DB,
        decode_responses: Literal[False, True] = True,
    ):
        self.host = host
        self.port = port
        self.db = db
        self.decode_responses = decode_responses

    def get_connection(self) -> Redis | None:
        if not all((self.host, self.port, self.db)):
            return None
        connection = Redis(host=self.host, port=self.port, db=self.db, decode_responses=self.decode_responses)
        try:
            connection.ping()
        except redis.exceptions.ConnectionError as err:
            logger.error(f"Отсуствует подключение к редису: {err}")
            return None
        return connection

    async def get_async_connection(self) -> AsyncRedis | None:
        if not all((self.host, self.port, self.db)):
            return None
        connection = AsyncRedis(host=self.host, port=self.port, db=self.db, decode_responses=self.decode_responses)
        try:
            await connection.ping()
        except redis.exceptions.ConnectionError as err:
            logger.error(f"Отсуствует подключение к редису: {err}")
            return None
        return connection


class RedisConnectorFactory:
    @classmethod
    def create(
        cls,
        host: str | None = settings.redis.REDIS_HOST,
        port: int | None = settings.redis.REDIS_PORT,
        db: int | None = settings.redis.REDIS_DB,
        decode_responses: Literal[False, True] = True,
    ):
        return RedisConnector(host=host, port=port, db=db, decode_responses=decode_responses)
