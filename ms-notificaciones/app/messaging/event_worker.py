import asyncio
import logging
import os

from app.messaging.notification_event_handlers import EVENT_HANDLERS
from shared.agm_messaging.contracts import (
    COMMUNICATION_MODE_GRPC,
    EVENT_ROUTING_KEYS_BY_TARGET,
    QUEUE_NOTIFICACIONES_EVENTS,
    SERVICE_NOTIFICACIONES,
)
from shared.agm_messaging.event_consumer import EventConsumer

logger = logging.getLogger(__name__)


async def start_event_worker() -> None:
    communication_mode = os.getenv("COMMUNICATION_MODE", "hybrid").lower()
    if communication_mode == COMMUNICATION_MODE_GRPC:
        logger.info("COMMUNICATION_MODE=grpc. Notificaciones RabbitMQ event worker disabled.")
        return

    retry_seconds = 5

    while True:
        try:
            consumer = EventConsumer(queue_name=QUEUE_NOTIFICACIONES_EVENTS)
            for routing_key in EVENT_ROUTING_KEYS_BY_TARGET[SERVICE_NOTIFICACIONES]:
                consumer.register_handler(routing_key, EVENT_HANDLERS[routing_key])

            logger.info(
                "Notificaciones RabbitMQ event worker listening on %s",
                QUEUE_NOTIFICACIONES_EVENTS,
            )
            print(
                f"Notificaciones RabbitMQ event worker listening on {QUEUE_NOTIFICACIONES_EVENTS}",
                flush=True,
            )
            await consumer.start()
            retry_seconds = 5
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.error(
                "Notificaciones RabbitMQ event worker failed: %s. Retrying in %ss...",
                exc,
                retry_seconds,
            )
            await asyncio.sleep(retry_seconds)
            retry_seconds = min(retry_seconds * 2, 30)
