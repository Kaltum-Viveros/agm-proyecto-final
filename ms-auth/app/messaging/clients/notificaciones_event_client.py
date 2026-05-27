import logging

from shared.agm_messaging.contracts import (
    EVENT_NOTIFICACIONES_RESET_PASSWORD,
    SERVICE_AUTH,
)
from shared.agm_messaging.event_publisher import EventPublisher

logger = logging.getLogger(__name__)


class NotificacionesEventClient:
    def __init__(self) -> None:
        self._publisher = EventPublisher(source=SERVICE_AUTH)

    async def publish_reset_password(
        self,
        usuario_id: str,
        email: str,
        reset_token: str,
    ) -> None:
        await self._publisher.publish(
            EVENT_NOTIFICACIONES_RESET_PASSWORD,
            {
                "usuario_id": str(usuario_id),
                "email": email,
                "reset_token": reset_token,
            },
        )
        logger.info("[NotificacionesEventClient] reset_password event published")


notificaciones_event_client = NotificacionesEventClient()
