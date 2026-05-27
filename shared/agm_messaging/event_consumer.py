import asyncio
import logging
import traceback
from typing import Any, Callable

import aio_pika

from .config import config
from .connection import RabbitMQConnection
from .contracts import QUEUE_NOTIFICACIONES_EVENTS, QUEUE_NOTIFICACIONES_EVENTS_DLQ
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
        dlx_exchange_name: str = config.EXCHANGE_EVENTS_DLX,
        prefetch_count: int = 1,
    ) -> None:
        self.queue_name = queue_name
        self.exchange_name = exchange_name
        self.dlx_exchange_name = dlx_exchange_name
        self.prefetch_count = prefetch_count
        self.dlq_name = self._dlq_name_for(queue_name)
        self.dlq_routing_key = self.dlq_name
        self.handlers: dict[str, Callable[[dict[str, Any]], Any]] = {}
        self.channel: aio_pika.Channel | None = None
        self._is_running = False

    def register_handler(self, routing_key: str, handler: Callable[[dict[str, Any]], Any]) -> None:
        self.handlers[routing_key] = handler

    async def start(self) -> None:
        connection = await RabbitMQConnection.get_connection()
        self.channel = await connection.channel()
        await self.channel.set_qos(prefetch_count=self.prefetch_count)

        exchange, queue = await self._declare_topology(connection)

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

    async def _declare_topology(
        self,
        connection: aio_pika.RobustConnection,
    ) -> tuple[aio_pika.abc.AbstractExchange, aio_pika.abc.AbstractQueue]:
        exchange = await self.channel.declare_exchange(
            self.exchange_name,
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )
        dlx = await self.channel.declare_exchange(
            self.dlx_exchange_name,
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )
        dlq = await self.channel.declare_queue(self.dlq_name, durable=True)
        await dlq.bind(dlx, routing_key=self.dlq_routing_key)

        queue_args = {
            "x-dead-letter-exchange": self.dlx_exchange_name,
            "x-dead-letter-routing-key": self.dlq_routing_key,
        }
        try:
            queue = await self.channel.declare_queue(
                self.queue_name,
                durable=True,
                arguments=queue_args,
            )
        except Exception as exc:
            if "PRECONDITION_FAILED" not in str(exc) and "inequivalent arg" not in str(exc):
                raise

            logger.warning(
                "[EventConsumer] Queue %s exists without DLQ args. "
                "Trying to migrate it if empty. error=%s",
                self.queue_name,
                exc,
            )
            if self.channel and not self.channel.is_closed:
                await self.channel.close()
            self.channel = await connection.channel()
            await self.channel.set_qos(prefetch_count=self.prefetch_count)
            exchange = await self.channel.declare_exchange(
                self.exchange_name,
                aio_pika.ExchangeType.TOPIC,
                durable=True,
            )
            dlx = await self.channel.declare_exchange(
                self.dlx_exchange_name,
                aio_pika.ExchangeType.TOPIC,
                durable=True,
            )
            dlq = await self.channel.declare_queue(self.dlq_name, durable=True)
            await dlq.bind(dlx, routing_key=self.dlq_routing_key)
            await self.channel.queue_delete(self.queue_name, if_empty=True)
            queue = await self.channel.declare_queue(
                self.queue_name,
                durable=True,
                arguments=queue_args,
            )
            logger.info("[EventConsumer] Queue %s migrated with DLQ args", self.queue_name)

        logger.info(
            "[EventConsumer] topology ready exchange=%s queue=%s dlx=%s dlq=%s prefetch=%s",
            self.exchange_name,
            self.queue_name,
            self.dlx_exchange_name,
            self.dlq_name,
            self.prefetch_count,
        )
        return exchange, queue

    async def _process_message(self, message: aio_pika.abc.AbstractIncomingMessage) -> None:
        event_type = message.type or message.routing_key
        correlation_id = message.correlation_id or message.message_id
        try:
            envelope = MessageEnvelope.deserialize(message.body)
            event_type = envelope.type or message.type or message.routing_key
            correlation_id = envelope.correlation_id or message.correlation_id or envelope.message_id

            if not event_type or event_type not in self.handlers:
                logger.warning(
                    "[EventConsumer] no handler routing_key=%s correlation_id=%s",
                    event_type,
                    correlation_id,
                )
                await message.reject(requeue=False)
                return

            handler = self.handlers[event_type]
            payload = envelope.data or {}
            try:
                logger.info(
                    "[EventConsumer] event received routing_key=%s correlation_id=%s",
                    event_type,
                    correlation_id,
                )
                if asyncio.iscoroutinefunction(handler):
                    await handler(payload)
                else:
                    await asyncio.to_thread(handler, payload)
                await message.ack()
                logger.info(
                    "[EventConsumer] event processed routing_key=%s correlation_id=%s",
                    event_type,
                    correlation_id,
                )
            except Exception as exc:
                logger.error(
                    "[EventConsumer] event failed, rejecting to DLQ routing_key=%s "
                    "correlation_id=%s error=%s",
                    event_type,
                    correlation_id,
                    exc,
                )
                traceback.print_exc()
                await message.reject(requeue=False)
        except Exception as exc:
            logger.error(
                "[EventConsumer] critical decode error, rejecting to DLQ "
                "routing_key=%s correlation_id=%s error=%s",
                event_type,
                correlation_id,
                exc,
            )
            traceback.print_exc()
            await message.reject(requeue=False)

    @staticmethod
    def _dlq_name_for(queue_name: str) -> str:
        if queue_name == QUEUE_NOTIFICACIONES_EVENTS:
            return QUEUE_NOTIFICACIONES_EVENTS_DLQ
        return f"{queue_name}.dlq"


EventConsumer = BaseEventConsumer
