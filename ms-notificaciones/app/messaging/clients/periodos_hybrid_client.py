import asyncio
import logging
import os

import aio_pika.exceptions
import aiormq.exceptions

from app.grpc.clients.materias_client import MateriasClient
from app.messaging.clients.periodos_rabbit_client import PeriodosRabbitClient
from shared.agm_messaging.exceptions import RPCException, RPCTimeoutException

logger = logging.getLogger(__name__)

_TRANSPORT_EXCEPTIONS = (
    TimeoutError,
    ConnectionError,
    OSError,
    RuntimeError,
    RPCException,
    RPCTimeoutException,
    aio_pika.exceptions.AMQPException,
    aiormq.exceptions.AMQPError,
)


class PeriodosHybridClient:
    """RabbitMQ primero y fallback gRPC hacia MS-2 para MS-6."""

    def __init__(self) -> None:
        self._rabbit = PeriodosRabbitClient()
        self._grpc = MateriasClient()
        self._mode = os.getenv("COMMUNICATION_MODE", "hybrid").lower()
        logger.info("[PeriodosHybridClient] COMMUNICATION_MODE=%s", self._mode)

    async def obtener_materia_async(self, materia_id: str) -> dict:
        if self._mode == "grpc":
            return await asyncio.to_thread(self._grpc.obtener_materia, materia_id)

        if self._mode == "rabbit":
            return await self._rabbit.obtener_materia(materia_id)

        try:
            return await self._rabbit.obtener_materia(materia_id)
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning(
                "[PeriodosHybridClient] RabbitMQ RPC failed, falling back to gRPC: %s",
                exc,
            )
            return await asyncio.to_thread(self._grpc.obtener_materia, materia_id)

    def obtener_materia(self, materia_id: str) -> dict:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.obtener_materia_async(materia_id))

        logger.warning(
            "[PeriodosHybridClient] Active event loop detected in sync call; using gRPC"
        )
        return self._grpc.obtener_materia(materia_id)


materias_client = PeriodosHybridClient()
