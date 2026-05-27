import logging

from shared.agm_messaging.contracts import (
    EVENT_NOTIFICACIONES_CIERRE_MATERIA,
    SERVICE_CALIFICACIONES,
)
from shared.agm_messaging.event_publisher import EventPublisher

logger = logging.getLogger(__name__)


class NotificacionesEventClient:
    def __init__(self) -> None:
        self._publisher = EventPublisher(source=SERVICE_CALIFICACIONES)

    async def publish_cierre_materia(self, materia_id: str) -> None:
        await self._publisher.publish(
            EVENT_NOTIFICACIONES_CIERRE_MATERIA,
            {
                "materia_id": str(materia_id),
            },
        )
        logger.info("[NotificacionesEventClient] cierre_materia event published")


notificaciones_event_client = NotificacionesEventClient()
