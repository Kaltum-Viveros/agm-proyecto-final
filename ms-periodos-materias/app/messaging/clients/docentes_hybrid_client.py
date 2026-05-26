import asyncio
import logging
import os

import aio_pika.exceptions
import aiormq.exceptions

from app.grpc.clients.docentes_client import DocentesClient
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
    """RabbitMQ primero y fallback gRPC hacia MS-3 para MS-2."""

    def __init__(self) -> None:
        self._rabbit = DocentesRabbitClient()
        self._grpc = DocentesClient()
        self._mode = os.getenv("COMMUNICATION_MODE", "hybrid").lower()
        logger.info("[DocentesHybridClient] COMMUNICATION_MODE=%s", self._mode)

    async def verificar_docente_async(self, docente_id: str) -> bool:
        if self._mode == "grpc":
            return await asyncio.to_thread(self._grpc.verificar_docente, docente_id)
        if self._mode == "rabbit":
            return await self._rabbit.verificar_docente(docente_id)
        try:
            return await self._rabbit.verificar_docente(docente_id)
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning("[DocentesHybridClient] RabbitMQ RPC failed, falling back to gRPC: %s", exc)
            return await asyncio.to_thread(self._grpc.verificar_docente, docente_id)

    async def resolver_docente_por_nombre_async(self, nombre_completo: str) -> str | None:
        if self._mode == "grpc":
            return await asyncio.to_thread(self._grpc.resolver_docente_por_nombre, nombre_completo)
        if self._mode == "rabbit":
            return await self._rabbit.resolver_docente_por_nombre(nombre_completo)
        try:
            return await self._rabbit.resolver_docente_por_nombre(nombre_completo)
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning("[DocentesHybridClient] RabbitMQ RPC failed, falling back to gRPC: %s", exc)
            return await asyncio.to_thread(self._grpc.resolver_docente_por_nombre, nombre_completo)

    def verificar_docente(self, docente_id: str) -> bool:
        return self._run_sync(self.verificar_docente_async(docente_id), self._grpc.verificar_docente, docente_id)

    def resolver_docente_por_nombre(self, nombre_completo: str) -> str | None:
        return self._run_sync(
            self.resolver_docente_por_nombre_async(nombre_completo),
            self._grpc.resolver_docente_por_nombre,
            nombre_completo,
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


docentes_client = DocentesHybridClient()
