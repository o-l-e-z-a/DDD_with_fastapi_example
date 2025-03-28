from dataclasses import dataclass
from typing import Any, Generic, TypeVar


@dataclass
class ClientParams: ...


P = TypeVar("P", bound=ClientParams)


class Client(Generic[P]):
    async def get(self, params: P) -> Any: ...

    async def send(self, params: P) -> dict[str, Any]: ...
