import asyncio
import logging
import os
from typing import Tuple

import aio_pika.exceptions
import aiormq.exceptions

from app.grpc.clients.auth_client import AuthClient
from app.messaging.clients.auth_rabbit_client import AuthRabbitClient
from shared.agm_messaging.exceptions import RPCException, RPCTimeoutException

logger = logging.getLogger(__name__)

_TRANSPORT_EXCEPTIONS = (
    RPCException,
    RPCTimeoutException,
    ConnectionError,
    OSError,
    RuntimeError,
    TimeoutError,
    aio_pika.exceptions.AMQPException,
    aiormq.exceptions.AMQPError,
)


class AuthHybridClient:
    """
    Cliente Auth para MS-3.

    rabbit: solo RabbitMQ.
    grpc: solo gRPC.
    hybrid: RabbitMQ primero y fallback gRPC solo ante errores de transporte.
    """

    def __init__(self) -> None:
        self._rabbit = AuthRabbitClient()
        self._grpc = AuthClient()
        self._mode = os.getenv("COMMUNICATION_MODE", "hybrid").lower()
        logger.info("[AuthHybridClient] COMMUNICATION_MODE=%s", self._mode)

    async def validate_token(self, token: str):
        if self._mode == "grpc":
            return await asyncio.to_thread(self._grpc.validate_token, token)

        if self._mode == "rabbit":
            return await self._rabbit.validate_token(token)

        try:
            return await self._rabbit.validate_token(token)
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning(
                "Auth RabbitMQ RPC failed, falling back to gRPC: %s",
                exc,
            )
            return await asyncio.to_thread(self._grpc.validate_token, token)

    async def check_role(self, user_id: str, role: str) -> bool:
        if self._mode == "grpc":
            return await asyncio.to_thread(self._grpc.check_role, user_id, role)

        if self._mode == "rabbit":
            return await self._rabbit.check_role(user_id, role)

        try:
            return await self._rabbit.check_role(user_id, role)
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning(
                "Auth RabbitMQ RPC failed, falling back to gRPC: %s",
                exc,
            )
            return await asyncio.to_thread(self._grpc.check_role, user_id, role)

    async def get_user_by_id(self, user_id: str):
        if self._mode == "grpc":
            return await asyncio.to_thread(self._grpc.get_user_by_id, user_id)

        if self._mode == "rabbit":
            return await self._rabbit.get_user_by_id(user_id)

        try:
            return await self._rabbit.get_user_by_id(user_id)
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning(
                "Auth RabbitMQ RPC failed, falling back to gRPC: %s",
                exc,
            )
            return await asyncio.to_thread(self._grpc.get_user_by_id, user_id)

    async def create_or_get_user_identity(
        self,
        nombre: str,
        email: str,
        role: str = "Alumno",
    ) -> Tuple[str | None, str | None]:
        if self._mode == "grpc":
            return await asyncio.to_thread(self._grpc.crear_identidad, nombre, email, role)

        if self._mode == "rabbit":
            return await self._rabbit.create_or_get_user_identity(nombre, email, role)

        try:
            return await self._rabbit.create_or_get_user_identity(nombre, email, role)
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning(
                "Auth RabbitMQ RPC failed, falling back to gRPC: %s",
                exc,
            )
            return await asyncio.to_thread(self._grpc.crear_identidad, nombre, email, role)

    def crear_identidad(
        self,
        nombre: str,
        email: str,
        role: str = "Alumno",
    ) -> Tuple[str | None, str | None]:
        return asyncio.run(self.create_or_get_user_identity(nombre, email, role))


auth_client = AuthHybridClient()
