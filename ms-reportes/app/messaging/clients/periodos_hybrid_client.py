import asyncio
import logging
import os

import aio_pika.exceptions
import aiormq.exceptions

from app.grpc.clients.periodos_materias_client import PeriodosMateriasClient
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
    """RabbitMQ primero y fallback gRPC hacia MS-2 para MS-7."""

    def __init__(self) -> None:
        self._rabbit = PeriodosRabbitClient()
        self._grpc = PeriodosMateriasClient()
        self._mode = os.getenv("COMMUNICATION_MODE", "hybrid").lower()
        logger.info("[PeriodosHybridClient] COMMUNICATION_MODE=%s", self._mode)

    async def get_materia_by_id(self, materia_id: str):
        if self._mode == "grpc":
            return await asyncio.to_thread(self._grpc.get_materia_by_id, materia_id)

        if self._mode == "rabbit":
            return await self._rabbit.get_materia_by_id(materia_id)

        try:
            return await self._rabbit.get_materia_by_id(materia_id)
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning(
                "[PeriodosHybridClient] RabbitMQ RPC failed, falling back to gRPC: %s",
                exc,
            )
            return await asyncio.to_thread(self._grpc.get_materia_by_id, materia_id)

    async def get_materias_by_docente(self, docente_id: str):
        if self._mode == "grpc":
            return await asyncio.to_thread(self._grpc.get_materias_by_docente, docente_id)

        if self._mode == "rabbit":
            return await self._rabbit.get_materias_by_docente(docente_id)

        try:
            return await self._rabbit.get_materias_by_docente(docente_id)
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning(
                "[PeriodosHybridClient] RabbitMQ RPC failed, falling back to gRPC: %s",
                exc,
            )
            return await asyncio.to_thread(self._grpc.get_materias_by_docente, docente_id)

    async def get_periodo_activo(self):
        if self._mode == "grpc":
            return await asyncio.to_thread(self._grpc.get_periodo_activo)

        if self._mode == "rabbit":
            return await self._rabbit.get_periodo_activo()

        try:
            return await self._rabbit.get_periodo_activo()
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning(
                "[PeriodosHybridClient] RabbitMQ RPC failed, falling back to gRPC: %s",
                exc,
            )
            return await asyncio.to_thread(self._grpc.get_periodo_activo)


periodos_materias_client = PeriodosHybridClient()
