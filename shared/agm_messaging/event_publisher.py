import asyncio
import logging
import uuid
from typing import Any

import aio_pika

from .config import config
from .envelope import MessageEnvelope

logger = logging.getLogger(__name__)


class BaseEventPublisher:
    """
    Publicador base de eventos RabbitMQ.
    """

    def __init__(
        self,
        exchange_name: str = config.EXCHANGE_EVENTS,
        source: str | None = None,
    ) -> None:
        self.exchange_name = exchange_name
        self.source = source

    async def connect(self) -> None:
        return None

    async def publish(
        self,
        routing_key: str,
        data: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        connection = None
        channel = None
        correlation_id = (metadata or {}).get("correlation_id") or str(uuid.uuid4())
        message_id = (metadata or {}).get("message_id") or str(uuid.uuid4())
        try:
            connection = await asyncio.wait_for(
                aio_pika.connect(config.URL),
                timeout=config.RPC_TIMEOUT,
            )
            channel = await connection.channel()
            exchange = await channel.declare_exchange(
                self.exchange_name,
                aio_pika.ExchangeType.TOPIC,
                durable=True,
            )
            envelope = MessageEnvelope(
                data=data,
                metadata=metadata,
                message_id=message_id,
                correlation_id=correlation_id,
                source=self.source,
                target=None,
                type=routing_key,
            )
            await asyncio.wait_for(
                exchange.publish(
                    aio_pika.Message(
                        body=envelope.serialize(),
                        type=routing_key,
                        message_id=message_id,
                        correlation_id=correlation_id,
                        headers={
                            "source": self.source or "",
                            "routing_key": routing_key,
                        },
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    ),
                    routing_key=routing_key,
                ),
                timeout=config.RPC_TIMEOUT,
            )
            logger.info(
                "[EventPublisher] event published routing_key=%s correlation_id=%s",
                routing_key,
                correlation_id,
            )
        except Exception as exc:
            error_detail = f"{type(exc).__name__}: {exc}"
            logger.warning(
                "[EventPublisher] publish failed routing_key=%s correlation_id=%s error=%s",
                routing_key,
                correlation_id,
                error_detail,
            )
            raise RuntimeError(error_detail) from exc
        finally:
            if channel and not channel.is_closed:
                await channel.close()
            if connection and not connection.is_closed:
                await connection.close()

    async def close(self) -> None:
        return None


EventPublisher = BaseEventPublisher
