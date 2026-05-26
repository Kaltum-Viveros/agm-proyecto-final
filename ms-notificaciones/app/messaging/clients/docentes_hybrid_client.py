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
    """RabbitMQ primero y fallback gRPC hacia MS-3 para MS-6."""

    def __init__(self) -> None:
        self._rabbit = DocentesRabbitClient()
        self._grpc = AlumnosClient()
        self._mode = os.getenv("COMMUNICATION_MODE", "hybrid").lower()
        logger.info("[DocentesHybridClient] COMMUNICATION_MODE=%s", self._mode)

    async def obtener_alumno_async(self, alumno_id: str) -> dict:
        if self._mode == "grpc":
            return await asyncio.to_thread(self._grpc.obtener_alumno, alumno_id)
        if self._mode == "rabbit":
            return await self._rabbit.obtener_alumno(alumno_id)
        try:
            return await self._rabbit.obtener_alumno(alumno_id)
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning("[DocentesHybridClient] RabbitMQ RPC failed, falling back to gRPC: %s", exc)
            return await asyncio.to_thread(self._grpc.obtener_alumno, alumno_id)

    async def obtener_docente_async(self, docente_id: str) -> dict:
        if self._mode == "grpc":
            return await asyncio.to_thread(self._grpc.obtener_docente, docente_id)
        if self._mode == "rabbit":
            return await self._rabbit.obtener_docente(docente_id)
        try:
            return await self._rabbit.obtener_docente(docente_id)
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning("[DocentesHybridClient] RabbitMQ RPC failed, falling back to gRPC: %s", exc)
            return await asyncio.to_thread(self._grpc.obtener_docente, docente_id)

    async def obtener_alumnos_por_materia_async(self, materia_id: str) -> list:
        if self._mode == "grpc":
            return await asyncio.to_thread(self._grpc.obtener_alumnos_por_materia, materia_id)
        if self._mode == "rabbit":
            return await self._rabbit.obtener_alumnos_por_materia(materia_id)
        try:
            return await self._rabbit.obtener_alumnos_por_materia(materia_id)
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning("[DocentesHybridClient] RabbitMQ RPC failed, falling back to gRPC: %s", exc)
            return await asyncio.to_thread(self._grpc.obtener_alumnos_por_materia, materia_id)

    def obtener_alumno(self, alumno_id: str) -> dict:
        return self._run_sync(self.obtener_alumno_async(alumno_id), self._grpc.obtener_alumno, alumno_id)

    def obtener_docente(self, docente_id: str) -> dict:
        return self._run_sync(self.obtener_docente_async(docente_id), self._grpc.obtener_docente, docente_id)

    def obtener_alumnos_por_materia(self, materia_id: str) -> list:
        return self._run_sync(
            self.obtener_alumnos_por_materia_async(materia_id),
            self._grpc.obtener_alumnos_por_materia,
            materia_id,
        )

    def _run_sync(self, coro, grpc_func, *args):
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            self._rabbit = DocentesRabbitClient()
            return asyncio.run(coro)

        logger.warning("[DocentesHybridClient] Active event loop detected in sync call; using gRPC")
        coro.close()
        return grpc_func(*args)


alumnos_client = DocentesHybridClient()
