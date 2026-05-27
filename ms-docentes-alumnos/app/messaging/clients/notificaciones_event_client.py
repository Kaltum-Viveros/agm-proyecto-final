import logging

from shared.agm_messaging.contracts import (
    EVENT_NOTIFICACIONES_BAJA_ALUMNO,
    EVENT_NOTIFICACIONES_BIENVENIDA_ALUMNO,
    SERVICE_DOCENTES_ALUMNOS,
)
from shared.agm_messaging.event_publisher import EventPublisher

logger = logging.getLogger(__name__)


class NotificacionesEventClient:
    def __init__(self) -> None:
        self._publisher = EventPublisher(source=SERVICE_DOCENTES_ALUMNOS)

    async def publish_bienvenida_alumno(
        self,
        alumno_id: str,
        materia_id: str,
        password_temporal: str,
    ) -> None:
        await self._publisher.publish(
            EVENT_NOTIFICACIONES_BIENVENIDA_ALUMNO,
            {
                "alumno_id": str(alumno_id),
                "materia_id": str(materia_id) if materia_id else "",
                "password_temporal": password_temporal,
            },
        )
        logger.info("[NotificacionesEventClient] bienvenida_alumno event published")

    async def publish_baja_alumno(
        self,
        alumno_id: str,
        docente_id: str,
        materia_id: str,
    ) -> None:
        await self._publisher.publish(
            EVENT_NOTIFICACIONES_BAJA_ALUMNO,
            {
                "alumno_id": str(alumno_id),
                "docente_id": str(docente_id),
                "materia_id": str(materia_id),
            },
        )
        logger.info("[NotificacionesEventClient] baja_alumno event published")


notificaciones_event_client = NotificacionesEventClient()
