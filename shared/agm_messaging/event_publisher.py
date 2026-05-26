from typing import Any

import aio_pika

from .config import config
from .connection import RabbitMQConnection
from .envelope import MessageEnvelope


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
        self.channel: aio_pika.Channel | None = None

    async def connect(self) -> None:
        connection = await RabbitMQConnection.get_connection()
        self.channel = await connection.channel()

    async def publish(
        self,
        routing_key: str,
        data: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        if not self.channel or self.channel.is_closed:
            await self.connect()

        exchange = await self.channel.declare_exchange(
            self.exchange_name,
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )
        envelope = MessageEnvelope(
            data=data,
            metadata=metadata,
            source=self.source,
            target=None,
            type=routing_key,
        )
        await exchange.publish(
            aio_pika.Message(
                body=envelope.serialize(),
                type=routing_key,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=routing_key,
        )

    async def close(self) -> None:
        if self.channel and not self.channel.is_closed:
            await self.channel.close()


EventPublisher = BaseEventPublisher
