import asyncio
import enum

from dataclasses import dataclass
from pprint import pprint
from typing import Any, Awaitable, Callable

import httpx

from httpx import AsyncClient
from hyx.circuitbreaker import consecutive_breaker, exceptions

from src.infrastructure.other_service_integration.base import ServiceNotAvailableError
from src.infrastructure.other_service_integration.client_interface import Client, ClientParams

breaker = consecutive_breaker(
    failure_threshold=5,
    recovery_time_secs=30,
)


class NotValidMethod(Exception):
    pass


class HTTPMethod(enum.Enum):
    GET = enum.auto()
    POST = enum.auto()
    DELETE = enum.auto()
    PUT = enum.auto()
    PATCH = enum.auto()


@dataclass
class HTTPParams(ClientParams):
    url: str
    method: HTTPMethod = HTTPMethod.GET
    headers: dict[str, str] | None = None
    body: Any | None = None
    query_params: Any | None = None


class HTTPClientAdapter(Client[HTTPParams]):
    async def get(self, params: HTTPParams) -> Any:
        try:
            return await self.send_request(params)
        except exceptions.BreakerFailing:
            raise ServiceNotAvailableError

    async def send(self, params: HTTPParams) -> dict[str, Any]: ...

    def _get_client_method_by_type(self, client: AsyncClient, method: HTTPMethod) -> Callable[..., Awaitable[Any]]:
        if method == HTTPMethod.GET:
            return client.get
        elif method == HTTPMethod.POST:
            return client.post
        elif method == HTTPMethod.DELETE:
            return client.delete
        elif method == HTTPMethod.PUT:
            return client.put
        elif method == HTTPMethod.PATCH:
            return client.patch
        raise NotValidMethod()

    async def send_request(self, params: HTTPParams) -> Any:
        async with breaker, httpx.AsyncClient() as client:
            try:
                if params.method != HTTPMethod.GET:
                    raise ServiceNotAvailableError
                client_method = self._get_client_method_by_type(client=client, method=params.method)
                response = await client_method(params.url, params=params.query_params)
                response.raise_for_status()
            except httpx.HTTPError:
                raise ServiceNotAvailableError
            return response.json()


async def client_get():
    # async with breaker:
    client = HTTPClientAdapter()
    for i in range(100):
        try:
            param = HTTPParams(
                url="http://127.0.0.1:8000/api/services/",
                query_params={"services_id": [1, 2, 3]},
                method=HTTPMethod.GET,
            )
            res = await client.get(param)
        except ServiceNotAvailableError as err:
            print("error", err)
        else:
            pprint(res)


if __name__ == "__main__":
    asyncio.run(client_get())
