import asyncio
import logging
import os

import aio_pika.exceptions
import aiormq.exceptions

from app.grpc.clients.calificaciones_client import CalificacionesClient
from app.messaging.clients.calificaciones_rabbit_client import CalificacionesRabbitClient
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


class CalificacionesHybridClient:
    """RabbitMQ primero y fallback gRPC hacia MS-4 para MS-7."""

    def __init__(self) -> None:
        self._rabbit = CalificacionesRabbitClient()
        self._grpc = CalificacionesClient()
        self._mode = os.getenv("COMMUNICATION_MODE", "hybrid").lower()
        logger.info("[CalificacionesHybridClient] COMMUNICATION_MODE=%s", self._mode)

    async def get_concentrado(self, materia_id: str, modo: str = "actual"):
        if self._mode == "grpc":
            return await asyncio.to_thread(self._grpc.get_concentrado, materia_id, modo)
        if self._mode == "rabbit":
            return await self._rabbit.get_concentrado(materia_id, modo)
        try:
            return await self._rabbit.get_concentrado(materia_id, modo)
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning("[CalificacionesHybridClient] RabbitMQ RPC failed, falling back to gRPC: %s", exc)
            return await asyncio.to_thread(self._grpc.get_concentrado, materia_id, modo)

    async def get_promedio_alumno(
        self,
        alumno_id: str,
        materia_id: str | None = None,
        modo: str = "actual",
    ):
        if self._mode == "grpc":
            return await asyncio.to_thread(self._grpc.get_promedio_alumno, alumno_id, materia_id or "", modo)
        if self._mode == "rabbit":
            return await self._rabbit.get_promedio_alumno(alumno_id, materia_id, modo)
        try:
            return await self._rabbit.get_promedio_alumno(alumno_id, materia_id, modo)
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning("[CalificacionesHybridClient] RabbitMQ RPC failed, falling back to gRPC: %s", exc)
            return await asyncio.to_thread(self._grpc.get_promedio_alumno, alumno_id, materia_id or "", modo)

    async def get_estadisticas_materia(self, materia_id: str, modo: str = "actual"):
        if self._mode == "grpc":
            return await asyncio.to_thread(self._grpc.get_estadisticas_materia, materia_id, modo)
        if self._mode == "rabbit":
            return await self._rabbit.get_estadisticas_materia(materia_id, modo)
        try:
            return await self._rabbit.get_estadisticas_materia(materia_id, modo)
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning("[CalificacionesHybridClient] RabbitMQ RPC failed, falling back to gRPC: %s", exc)
            return await asyncio.to_thread(self._grpc.get_estadisticas_materia, materia_id, modo)

    obtener_concentrado = get_concentrado
    obtener_promedio_alumno = get_promedio_alumno
    obtener_estadisticas_materia = get_estadisticas_materia
    get_promedio = get_promedio_alumno
    get_estadisticas = get_estadisticas_materia


calificaciones_client = CalificacionesHybridClient()
