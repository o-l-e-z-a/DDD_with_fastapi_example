from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Type

from src.logic.queries.base import QR, QT, BaseQuery, QueryHandler


@dataclass(eq=False)
class QueryMediator(ABC):
    queries_map: dict[Type[BaseQuery], QueryHandler] = field(
        default_factory=dict,
        kw_only=True,
    )

    @abstractmethod
    def register_query(self, query: Type[QT], query_handler: QueryHandler[QT, QR]) -> QR: ...

    @abstractmethod
    async def handle_query(self, query: BaseQuery) -> QR: ...
