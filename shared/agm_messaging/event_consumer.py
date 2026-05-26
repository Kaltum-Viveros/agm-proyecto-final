import asyncio
import logging
import traceback
from typing import Any, Callable

import aio_pika

from .config import config
from .connection import RabbitMQConnection
from .envelope import MessageEnvelope

logger = logging.getLogger(__name__)


class BaseEventConsumer:
    """
    Consumidor base de eventos RabbitMQ.
    """

    def __init__(
        self,
        queue_name: str,
        exchange_name: str = config.EXCHANGE_EVENTS,
    ) -> None:
        self.queue_name = queue_name
        self.exchange_name = exchange_name
        self.handlers: dict[str, Callable[[dict[str, Any]], Any]] = {}
        self.channel: aio_pika.Channel | None = None
        self._is_running = False

    def register_handler(self, routing_key: str, handler: Callable[[dict[str, Any]], Any]) -> None:
        self.handlers[routing_key] = handler

    async def start(self) -> None:
        connection = await RabbitMQConnection.get_connection()
        self.channel = await connection.channel()
        await self.channel.set_qos(prefetch_count=10)

        exchange = await self.channel.declare_exchange(
            self.exchange_name,
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )
        queue = await self.channel.declare_queue(self.queue_name, durable=True)

        for routing_key in self.handlers:
            await queue.bind(exchange, routing_key=routing_key)

        self._is_running = True
        logger.info("[*] Consumiendo eventos en la cola %s", self.queue_name)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                if not self._is_running:
                    break
                await self._process_message(message)

    async def stop(self) -> None:
        self._is_running = False
        if self.channel and not self.channel.is_closed:
            await self.channel.close()

    async def _process_message(self, message: aio_pika.abc.AbstractIncomingMessage) -> None:
        try:
            envelope = MessageEnvelope.deserialize(message.body)
            event_type = envelope.type or message.type or message.routing_key

            if not event_type or event_type not in self.handlers:
                logger.warning("No handler registered for event %s", event_type)
                await message.reject(requeue=False)
                return

            handler = self.handlers[event_type]
            payload = envelope.data or {}
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(payload)
                else:
                    await asyncio.to_thread(handler, payload)
                await message.ack()
            except Exception as exc:
                logger.error("Error processing event %s: %s", event_type, exc)
                traceback.print_exc()
                await message.reject(requeue=False)
        except Exception as exc:
            logger.error("Critical error decoding event: %s", exc)
            traceback.print_exc()
            await message.reject(requeue=False)


EventConsumer = BaseEventConsumer
