import asyncio
import logging
import os

import aio_pika.exceptions
import aiormq.exceptions

from app.grpc.clients.docentes_alumnos_client import DocentesAlumnosClient
from app.messaging.clients.docentes_rabbit_client import DocentesRabbitClient
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


class DocentesHybridClient:
    """RabbitMQ primero y fallback gRPC hacia MS-3 para MS-7."""

    def __init__(self) -> None:
        self._rabbit = DocentesRabbitClient()
        self._grpc = DocentesAlumnosClient()
        self._mode = os.getenv("COMMUNICATION_MODE", "hybrid").lower()
        logger.info("[DocentesHybridClient] COMMUNICATION_MODE=%s", self._mode)

    async def get_alumnos_by_materia(self, materia_id: str):
        if self._mode == "grpc":
            return await asyncio.to_thread(self._grpc.get_alumnos_by_materia, materia_id)
        if self._mode == "rabbit":
            return await self._rabbit.get_alumnos_by_materia(materia_id)
        try:
            return await self._rabbit.get_alumnos_by_materia(materia_id)
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning("[DocentesHybridClient] RabbitMQ RPC failed, falling back to gRPC: %s", exc)
            return await asyncio.to_thread(self._grpc.get_alumnos_by_materia, materia_id)

    async def get_alumno_by_id(self, alumno_id: str):
        if self._mode == "grpc":
            return await asyncio.to_thread(self._grpc.get_alumno_by_id, alumno_id)
        if self._mode == "rabbit":
            return await self._rabbit.get_alumno_by_id(alumno_id)
        try:
            return await self._rabbit.get_alumno_by_id(alumno_id)
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning("[DocentesHybridClient] RabbitMQ RPC failed, falling back to gRPC: %s", exc)
            return await asyncio.to_thread(self._grpc.get_alumno_by_id, alumno_id)

    async def get_materias_by_alumno(self, alumno_id: str):
        if self._mode == "grpc":
            return await asyncio.to_thread(self._grpc.get_materias_by_alumno, alumno_id)
        if self._mode == "rabbit":
            return await self._rabbit.get_materias_by_alumno(alumno_id)
        try:
            return await self._rabbit.get_materias_by_alumno(alumno_id)
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning("[DocentesHybridClient] RabbitMQ RPC failed, falling back to gRPC: %s", exc)
            return await asyncio.to_thread(self._grpc.get_materias_by_alumno, alumno_id)


docentes_alumnos_client = DocentesHybridClient()
