import asyncio
import logging
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

from shared.agm_messaging.contracts import (
    EVENT_NOTIFICACIONES_BAJA_ALUMNO,
    SERVICE_NOTIFICACIONES,
)
from shared.agm_messaging.event_publisher import EventPublisher


logging.basicConfig(level=logging.INFO)


async def main() -> None:
    publisher = EventPublisher(source=SERVICE_NOTIFICACIONES)
    payload = {
        "alumno_id": "",
        "materia_id": "",
    }
    await publisher.publish(EVENT_NOTIFICACIONES_BAJA_ALUMNO, payload)
    print(f"Evento invalido publicado: {EVENT_NOTIFICACIONES_BAJA_ALUMNO}")
    print(payload)


if __name__ == "__main__":
    asyncio.run(main())
