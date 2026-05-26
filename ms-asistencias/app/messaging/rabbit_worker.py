import asyncio
import logging
import os

from shared.agm_messaging.contracts import (
    COMMUNICATION_MODE_GRPC,
    QUEUE_ASISTENCIAS_RPC,
    RPC_ASISTENCIAS_GET_ASISTENCIA_ALUMNO,
    RPC_ASISTENCIAS_GET_ASISTENCIAS_MATERIA,
    RPC_ASISTENCIAS_GET_ESTADISTICAS_ASISTENCIA,
    RPC_ROUTING_KEYS_BY_TARGET,
    SERVICE_ASISTENCIAS,
)
from shared.agm_messaging.rpc_server import RabbitRpcServer

from app.messaging.asistencias_rpc_handlers import (
    get_asistencia_alumno_handler,
    get_asistencias_materia_handler,
    get_estadisticas_asistencia_handler,
)

logger = logging.getLogger(__name__)

_HANDLERS = {
    RPC_ASISTENCIAS_GET_ASISTENCIA_ALUMNO: get_asistencia_alumno_handler,
    RPC_ASISTENCIAS_GET_ASISTENCIAS_MATERIA: get_asistencias_materia_handler,
    RPC_ASISTENCIAS_GET_ESTADISTICAS_ASISTENCIA: get_estadisticas_asistencia_handler,
}


async def start_rabbit_worker() -> None:
    communication_mode = os.getenv("COMMUNICATION_MODE", "hybrid").lower()
    if communication_mode == COMMUNICATION_MODE_GRPC:
        logger.info("COMMUNICATION_MODE=grpc. Asistencias RabbitMQ RPC worker disabled.")
        return

    retry_seconds = 5

    while True:
        try:
            server = RabbitRpcServer(queue_name=QUEUE_ASISTENCIAS_RPC)

            for routing_key in RPC_ROUTING_KEYS_BY_TARGET[SERVICE_ASISTENCIAS]:
                server.register_handler(routing_key, _HANDLERS[routing_key])

            logger.info(
                "Asistencias RabbitMQ RPC worker listening on %s",
                QUEUE_ASISTENCIAS_RPC,
            )
            print(
                f"Asistencias RabbitMQ RPC worker listening on {QUEUE_ASISTENCIAS_RPC}",
                flush=True,
            )
            await server.start()
            retry_seconds = 5
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.error(
                "Asistencias RabbitMQ RPC worker failed: %s. Retrying in %ss...",
                exc,
                retry_seconds,
            )
            await asyncio.sleep(retry_seconds)
            retry_seconds = min(retry_seconds * 2, 30)
