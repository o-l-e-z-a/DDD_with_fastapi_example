from dataclasses import asdict
from typing import Any

import orjson

from src.domain.base.events import BaseEvent


def convert_event_to_broker_message(event: BaseEvent) -> bytes:
    return orjson.dumps(event)


def convert_broker_message_to_dict(message_body: bytes) -> dict[str, Any]:
    return orjson.loads(message_body)


def convert_event_to_json(event: BaseEvent) -> dict[str, Any]:
    return asdict(event)
