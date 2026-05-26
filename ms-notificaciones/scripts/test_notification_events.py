import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

from shared.agm_messaging.connection import RabbitMQConnection
from shared.agm_messaging.contracts import (
    EVENT_NOTIFICACIONES_RESET_PASSWORD,
    SERVICE_NOTIFICACIONES,
)
from shared.agm_messaging.event_publisher import EventPublisher


async def main() -> None:
    publisher = EventPublisher(source="ms-notificaciones-test-script")
    payload = {
        "usuario_id": "00000000-0000-0000-0000-000000000000",
        "email": "correo_de_prueba@ejemplo.com",
        "reset_token": "token-prueba-evento",
    }
    try:
        await publisher.publish(
            EVENT_NOTIFICACIONES_RESET_PASSWORD,
            payload,
            metadata={"target": SERVICE_NOTIFICACIONES, "test": True},
        )
        print(f"Evento publicado: {EVENT_NOTIFICACIONES_RESET_PASSWORD}")
        print(f"Payload: {payload}")
        print("OK: evento de reset_password publicado.")
    finally:
        await publisher.close()
        await RabbitMQConnection.close()


if __name__ == "__main__":
    asyncio.run(main())
