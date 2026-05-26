import logging
import os

import aio_pika.exceptions
import aiormq.exceptions

from app.grpc_clients.cliente_alumnos import ClienteAlumnos
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
    """RabbitMQ primero y fallback gRPC hacia MS-3 para MS-5."""

    def __init__(self) -> None:
        self._rabbit = DocentesRabbitClient()
        self._grpc = ClienteAlumnos()
        self._mode = os.getenv("COMMUNICATION_MODE", "hybrid").lower()
        logger.info("[DocentesHybridClient] COMMUNICATION_MODE=%s", self._mode)

    async def verificar_alumno_en_materia(self, id_alumno: str, id_materia: str) -> bool:
        if self._mode == "grpc":
            return await self._grpc.verificar_alumno_en_materia(id_alumno, id_materia)
        if self._mode == "rabbit":
            return await self._rabbit.verificar_alumno_en_materia(id_alumno, id_materia)
        try:
            return await self._rabbit.verificar_alumno_en_materia(id_alumno, id_materia)
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning("[DocentesHybridClient] RabbitMQ RPC failed, falling back to gRPC: %s", exc)
            return await self._grpc.verificar_alumno_en_materia(id_alumno, id_materia)

    async def obtener_alumnos_por_materia(self, id_materia: str) -> list:
        if self._mode == "grpc":
            return await self._grpc.obtener_alumnos_por_materia(id_materia)
        if self._mode == "rabbit":
            return await self._rabbit.obtener_alumnos_por_materia(id_materia)
        try:
            return await self._rabbit.obtener_alumnos_por_materia(id_materia)
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning("[DocentesHybridClient] RabbitMQ RPC failed, falling back to gRPC: %s", exc)
            return await self._grpc.obtener_alumnos_por_materia(id_materia)

    async def obtener_docente_por_email(self, email: str):
        if self._mode == "grpc":
            return await self._grpc.obtener_docente_por_email(email)
        if self._mode == "rabbit":
            return await self._rabbit.obtener_docente_por_email(email)
        try:
            return await self._rabbit.obtener_docente_por_email(email)
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning("[DocentesHybridClient] RabbitMQ RPC failed, falling back to gRPC: %s", exc)
            return await self._grpc.obtener_docente_por_email(email)

    async def obtener_alumno_por_email(self, email: str):
        if self._mode == "grpc":
            return await self._grpc.obtener_alumno_por_email(email)
        if self._mode == "rabbit":
            return await self._rabbit.obtener_alumno_por_email(email)
        try:
            return await self._rabbit.obtener_alumno_por_email(email)
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning("[DocentesHybridClient] RabbitMQ RPC failed, falling back to gRPC: %s", exc)
            return await self._grpc.obtener_alumno_por_email(email)


cliente_alumnos = DocentesHybridClient()
