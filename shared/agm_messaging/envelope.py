import orjson
import uuid
from typing import Any, Dict, Optional
from datetime import datetime, timezone

class MessageEnvelope:
    def __init__(
        self, 
        data: Any, 
        metadata: Optional[Dict[str, Any]] = None,
        message_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        source: Optional[str] = None,
        target: Optional[str] = None,
        type: Optional[str] = None,
        timestamp: Optional[str] = None,
    ):
        self.data = data
        self.metadata = metadata or {}
        self.message_id = message_id or str(uuid.uuid4())
        self.correlation_id = correlation_id
        self.source = source
        self.target = target
        self.type = type
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()

    def serialize(self) -> bytes:
        return orjson.dumps({
            "message_id": self.message_id,
            "correlation_id": self.correlation_id,
            "source": self.source,
            "target": self.target,
            "type": self.type,
            "timestamp": self.timestamp,
            "data": self.data,
            "metadata": self.metadata
        })

    @classmethod
    def deserialize(cls, payload: bytes) -> 'MessageEnvelope':
        parsed = orjson.loads(payload)
        return cls(
            data=parsed.get("data"),
            metadata=parsed.get("metadata"),
            message_id=parsed.get("message_id"),
            correlation_id=parsed.get("correlation_id"),
            source=parsed.get("source"),
            target=parsed.get("target"),
            type=parsed.get("type"),
            timestamp=parsed.get("timestamp")
        )
