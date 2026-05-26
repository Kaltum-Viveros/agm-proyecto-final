import asyncio
import logging
import os

from shared.agm_messaging.contracts import (
    COMMUNICATION_MODE_GRPC,
    QUEUE_DOCENTES_ALUMNOS_RPC,
    RPC_DOCENTES_GET_ALUMNOS_BY_MATERIA,
    RPC_DOCENTES_IS_ALUMNO_EN_MATERIA,
    RPC_DOCENTES_GET_MATERIAS_BY_ALUMNO,
    RPC_DOCENTES_GET_ALUMNO_BY_ID,
    RPC_DOCENTES_GET_DOCENTE_BY_ID,
    RPC_DOCENTES_GET_DOCENTE_BY_NOMBRE,
    RPC_DOCENTES_GET_DOCENTE_BY_EMAIL,
    RPC_DOCENTES_GET_ALUMNO_BY_EMAIL,
    RPC_ROUTING_KEYS_BY_TARGET,
    SERVICE_DOCENTES_ALUMNOS,
)
from shared.agm_messaging.rpc_server import RabbitRpcServer

from app.messaging.docentes_rpc_handlers import (
    get_alumnos_by_materia_handler,
    is_alumno_en_materia_handler,
    get_materias_by_alumno_handler,
    get_alumno_by_id_handler,
    get_docente_by_id_handler,
    get_docente_by_nombre_handler,
    get_docente_by_email_handler,
    get_alumno_by_email_handler,
)

logger = logging.getLogger(__name__)

_HANDLERS = {
    RPC_DOCENTES_GET_ALUMNOS_BY_MATERIA: get_alumnos_by_materia_handler,
    RPC_DOCENTES_IS_ALUMNO_EN_MATERIA: is_alumno_en_materia_handler,
    RPC_DOCENTES_GET_MATERIAS_BY_ALUMNO: get_materias_by_alumno_handler,
    RPC_DOCENTES_GET_ALUMNO_BY_ID: get_alumno_by_id_handler,
    RPC_DOCENTES_GET_DOCENTE_BY_ID: get_docente_by_id_handler,
    RPC_DOCENTES_GET_DOCENTE_BY_NOMBRE: get_docente_by_nombre_handler,
    RPC_DOCENTES_GET_DOCENTE_BY_EMAIL: get_docente_by_email_handler,
    RPC_DOCENTES_GET_ALUMNO_BY_EMAIL: get_alumno_by_email_handler,
}


async def start_rabbit_worker() -> None:
    communication_mode = os.getenv("COMMUNICATION_MODE", "hybrid").lower()
    if communication_mode == COMMUNICATION_MODE_GRPC:
        logger.info(
            "COMMUNICATION_MODE=grpc. Docentes-Alumnos RabbitMQ RPC worker disabled."
        )
        return

    retry_seconds = 5

    while True:
        try:
            server = RabbitRpcServer(queue_name=QUEUE_DOCENTES_ALUMNOS_RPC)

            for routing_key in RPC_ROUTING_KEYS_BY_TARGET[SERVICE_DOCENTES_ALUMNOS]:
                server.register_handler(routing_key, _HANDLERS[routing_key])

            logger.info(
                "Docentes-Alumnos RabbitMQ RPC worker listening on %s",
                QUEUE_DOCENTES_ALUMNOS_RPC,
            )
            print(
                "Docentes-Alumnos RabbitMQ RPC worker listening on "
                f"{QUEUE_DOCENTES_ALUMNOS_RPC}",
                flush=True,
            )
            await server.start()
            retry_seconds = 5
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.error(
                "Docentes-Alumnos RabbitMQ RPC worker failed: %s. Retrying in %ss...",
                exc,
                retry_seconds,
            )
            await asyncio.sleep(retry_seconds)
            retry_seconds = min(retry_seconds * 2, 30)
