import asyncio
import logging
import os

from shared.agm_messaging.contracts import (
    COMMUNICATION_MODE_GRPC,
    QUEUE_CALIFICACIONES_RPC,
    RPC_CALIFICACIONES_GET_CONCENTRADO,
    RPC_CALIFICACIONES_GET_ESTADISTICAS_MATERIA,
    RPC_CALIFICACIONES_GET_PROMEDIO_ALUMNO,
    RPC_ROUTING_KEYS_BY_TARGET,
    SERVICE_CALIFICACIONES,
)
from shared.agm_messaging.rpc_server import RabbitRpcServer

from app.messaging.calificaciones_rpc_handlers import (
    get_concentrado_handler,
    get_estadisticas_materia_handler,
    get_promedio_alumno_handler,
)

logger = logging.getLogger(__name__)

_HANDLERS = {
    RPC_CALIFICACIONES_GET_CONCENTRADO: get_concentrado_handler,
    RPC_CALIFICACIONES_GET_PROMEDIO_ALUMNO: get_promedio_alumno_handler,
    RPC_CALIFICACIONES_GET_ESTADISTICAS_MATERIA: get_estadisticas_materia_handler,
}


async def start_rabbit_worker() -> None:
    communication_mode = os.getenv("COMMUNICATION_MODE", "hybrid").lower()
    if communication_mode == COMMUNICATION_MODE_GRPC:
        logger.info("COMMUNICATION_MODE=grpc. Calificaciones RabbitMQ RPC worker disabled.")
        return

    retry_seconds = 5

    while True:
        try:
            server = RabbitRpcServer(queue_name=QUEUE_CALIFICACIONES_RPC)

            for routing_key in RPC_ROUTING_KEYS_BY_TARGET[SERVICE_CALIFICACIONES]:
                server.register_handler(routing_key, _HANDLERS[routing_key])

            logger.info(
                "Calificaciones RabbitMQ RPC worker listening on %s",
                QUEUE_CALIFICACIONES_RPC,
            )
            print(
                f"Calificaciones RabbitMQ RPC worker listening on {QUEUE_CALIFICACIONES_RPC}",
                flush=True,
            )
            await server.start()
            retry_seconds = 5
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.error(
                "Calificaciones RabbitMQ RPC worker failed: %s. Retrying in %ss...",
                exc,
                retry_seconds,
            )
            await asyncio.sleep(retry_seconds)
            retry_seconds = min(retry_seconds * 2, 30)
