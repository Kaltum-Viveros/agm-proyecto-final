import asyncio
import logging
import os

from shared.agm_messaging.contracts import (
    COMMUNICATION_MODE_GRPC,
    QUEUE_PERIODOS_MATERIAS_RPC,
    RPC_PERIODOS_GET_MATERIA_BY_ID,
    RPC_PERIODOS_GET_MATERIA_BY_NRC,
    RPC_PERIODOS_GET_MATERIAS_BY_DOCENTE,
    RPC_PERIODOS_GET_PERIODO_ACTIVO,
    RPC_ROUTING_KEYS_BY_TARGET,
    SERVICE_PERIODOS_MATERIAS,
)
from shared.agm_messaging.rpc_server import RabbitRpcServer

from app.messaging.periodos_rpc_handlers import (
    get_materia_by_id_handler,
    get_materia_by_nrc_handler,
    get_materias_by_docente_handler,
    get_periodo_activo_handler,
)

logger = logging.getLogger(__name__)

_HANDLERS = {
    RPC_PERIODOS_GET_MATERIA_BY_ID: get_materia_by_id_handler,
    RPC_PERIODOS_GET_MATERIA_BY_NRC: get_materia_by_nrc_handler,
    RPC_PERIODOS_GET_MATERIAS_BY_DOCENTE: get_materias_by_docente_handler,
    RPC_PERIODOS_GET_PERIODO_ACTIVO: get_periodo_activo_handler,
}


async def start_rabbit_worker() -> None:
    communication_mode = os.getenv("COMMUNICATION_MODE", "hybrid").lower()
    if communication_mode == COMMUNICATION_MODE_GRPC:
        logger.info("COMMUNICATION_MODE=grpc. Periodos RabbitMQ RPC worker disabled.")
        return

    retry_seconds = 5

    while True:
        try:
            server = RabbitRpcServer(queue_name=QUEUE_PERIODOS_MATERIAS_RPC)

            for routing_key in RPC_ROUTING_KEYS_BY_TARGET[SERVICE_PERIODOS_MATERIAS]:
                server.register_handler(routing_key, _HANDLERS[routing_key])

            logger.info(
                "Periodos RabbitMQ RPC worker listening on %s",
                QUEUE_PERIODOS_MATERIAS_RPC,
            )
            print(
                f"Periodos RabbitMQ RPC worker listening on {QUEUE_PERIODOS_MATERIAS_RPC}",
                flush=True,
            )
            await server.start()
            retry_seconds = 5
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.error(
                "Periodos RabbitMQ RPC worker failed: %s. Retrying in %ss...",
                exc,
                retry_seconds,
            )
            await asyncio.sleep(retry_seconds)
            retry_seconds = min(retry_seconds * 2, 30)
