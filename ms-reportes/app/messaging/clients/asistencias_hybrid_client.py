import asyncio
import logging
import os

import aio_pika.exceptions
import aiormq.exceptions

from app.grpc.clients.asistencias_client import AsistenciasClient
from app.messaging.clients.asistencias_rabbit_client import AsistenciasRabbitClient
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


class AsistenciasHybridClient:
    """RabbitMQ primero y fallback gRPC hacia MS-5 para MS-7."""

    def __init__(self) -> None:
        self._rabbit = AsistenciasRabbitClient()
        self._grpc = AsistenciasClient()
        self._mode = os.getenv("COMMUNICATION_MODE", "hybrid").lower()
        logger.info("[AsistenciasHybridClient] COMMUNICATION_MODE=%s", self._mode)

    async def get_asistencia_alumno(self, id_alumno: str, id_materia: str):
        if self._mode == "grpc":
            return await asyncio.to_thread(self._grpc.get_asistencia_alumno, id_alumno, id_materia)
        if self._mode == "rabbit":
            return await self._rabbit.get_asistencia_alumno(id_alumno, id_materia)
        try:
            return await self._rabbit.get_asistencia_alumno(id_alumno, id_materia)
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning("[AsistenciasHybridClient] RabbitMQ RPC failed, falling back to gRPC: %s", exc)
            return await asyncio.to_thread(self._grpc.get_asistencia_alumno, id_alumno, id_materia)

    async def get_asistencias_materia(self, id_materia: str):
        if self._mode == "grpc":
            return await asyncio.to_thread(self._grpc.get_asistencias_materia, id_materia)
        if self._mode == "rabbit":
            return await self._rabbit.get_asistencias_materia(id_materia)
        try:
            return await self._rabbit.get_asistencias_materia(id_materia)
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning("[AsistenciasHybridClient] RabbitMQ RPC failed, falling back to gRPC: %s", exc)
            return await asyncio.to_thread(self._grpc.get_asistencias_materia, id_materia)

    async def get_estadisticas_asistencia(self, id_materia: str):
        if self._mode == "grpc":
            return await asyncio.to_thread(self._grpc.get_estadisticas_asistencia, id_materia)
        if self._mode == "rabbit":
            return await self._rabbit.get_estadisticas_asistencia(id_materia)
        try:
            return await self._rabbit.get_estadisticas_asistencia(id_materia)
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning("[AsistenciasHybridClient] RabbitMQ RPC failed, falling back to gRPC: %s", exc)
            return await asyncio.to_thread(self._grpc.get_estadisticas_asistencia, id_materia)

    obtener_asistencia_alumno = get_asistencia_alumno
    obtener_asistencias_materia = get_asistencias_materia
    obtener_estadisticas_asistencia = get_estadisticas_asistencia
    get_estadisticas = get_estadisticas_asistencia


asistencias_client = AsistenciasHybridClient()
