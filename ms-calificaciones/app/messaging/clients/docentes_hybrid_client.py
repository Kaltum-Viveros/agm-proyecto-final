import asyncio
import logging
import os

import aio_pika.exceptions
import aiormq.exceptions

from app.grpc.clients.alumnos_client import AlumnosClient
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
    """RabbitMQ primero y fallback gRPC hacia MS-3 para MS-4."""

    def __init__(self) -> None:
        self._rabbit = DocentesRabbitClient()
        self._grpc = AlumnosClient()
        self._mode = os.getenv("COMMUNICATION_MODE", "hybrid").lower()
        logger.info("[DocentesHybridClient] COMMUNICATION_MODE=%s", self._mode)

    async def is_alumno_en_materia_async(self, alumno_id: str, materia_id: str) -> bool:
        if self._mode == "grpc":
            return await asyncio.to_thread(self._grpc.is_alumno_en_materia, alumno_id, materia_id)
        if self._mode == "rabbit":
            return await self._rabbit.is_alumno_en_materia(alumno_id, materia_id)
        try:
            return await self._rabbit.is_alumno_en_materia(alumno_id, materia_id)
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning("[DocentesHybridClient] RabbitMQ RPC failed, falling back to gRPC: %s", exc)
            return await asyncio.to_thread(self._grpc.is_alumno_en_materia, alumno_id, materia_id)

    async def get_alumno_by_email_async(self, email: str):
        if self._mode == "grpc":
            return await asyncio.to_thread(self._grpc.get_alumno_by_email, email)
        if self._mode == "rabbit":
            return await self._rabbit.get_alumno_by_email(email)
        try:
            return await self._rabbit.get_alumno_by_email(email)
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning("[DocentesHybridClient] RabbitMQ RPC failed, falling back to gRPC: %s", exc)
            return await asyncio.to_thread(self._grpc.get_alumno_by_email, email)

    async def get_alumno_perfil_async(self, alumno_id: str):
        if self._mode == "grpc":
            return await asyncio.to_thread(self._grpc.get_alumno_perfil, alumno_id)
        if self._mode == "rabbit":
            return await self._rabbit.get_alumno_perfil(alumno_id)
        try:
            return await self._rabbit.get_alumno_perfil(alumno_id)
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning("[DocentesHybridClient] RabbitMQ RPC failed, falling back to gRPC: %s", exc)
            return await asyncio.to_thread(self._grpc.get_alumno_perfil, alumno_id)

    def is_alumno_en_materia(self, alumno_id: str, materia_id: str) -> bool:
        return self._run_sync(self.is_alumno_en_materia_async(alumno_id, materia_id))

    def get_alumno_by_email(self, email: str):
        return self._run_sync(self.get_alumno_by_email_async(email))

    def get_alumno_perfil(self, alumno_id: str):
        return self._run_sync(self.get_alumno_perfil_async(alumno_id))

    def _run_sync(self, coro):
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            self._rabbit = DocentesRabbitClient()
            return asyncio.run(coro)
        raise RuntimeError("DocentesHybridClient sync method called from active event loop")


alumnos_client = DocentesHybridClient()
