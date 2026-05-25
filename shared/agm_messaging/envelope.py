import json
import orjson
from typing import Any, Dict

class MessageEnvelope:
    def __init__(self, data: Any, metadata: Dict[str, Any] = None):
        self.data = data
        self.metadata = metadata or {}

    def serialize(self) -> bytes:
        return orjson.dumps({
            "data": self.data,
            "metadata": self.metadata
        })

    @classmethod
    def deserialize(cls, payload: bytes) -> 'MessageEnvelope':
        parsed = orjson.loads(payload)
        return cls(data=parsed.get("data"), metadata=parsed.get("metadata", {}))
