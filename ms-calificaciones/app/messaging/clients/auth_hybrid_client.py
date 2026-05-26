import asyncio
import logging
import os
from typing import Any, Dict, Optional

import aio_pika.exceptions
import aiormq.exceptions

from app.grpc.clients.auth_client import AuthClient
from app.messaging.clients.auth_rabbit_client import AuthRabbitClient
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


class AuthHybridClient:
    """
    Fachada Auth para MS-4.

    grpc: solo gRPC.
    rabbit: solo RabbitMQ.
    hybrid: RabbitMQ primero y fallback gRPC solo ante errores de transporte.
    """

    def __init__(self) -> None:
        self._rabbit = AuthRabbitClient()
        self._grpc = AuthClient()
        self._mode = os.getenv("COMMUNICATION_MODE", "hybrid").lower()
        logger.info("[AuthHybridClient] COMMUNICATION_MODE=%s", self._mode)

    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        if self._mode == "grpc":
            logger.debug("[AuthHybridClient] validate_token via gRPC")
            return await asyncio.to_thread(self._grpc.validate_token, token)

        if self._mode == "rabbit":
            logger.debug("[AuthHybridClient] validate_token via RabbitMQ")
            return await self._rabbit.validate_token(token)

        try:
            result = await self._rabbit.validate_token(token)
            logger.debug("[AuthHybridClient] validate_token via RabbitMQ OK")
            return result
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning(
                "[AuthHybridClient] Auth RabbitMQ RPC failed, falling back to gRPC: %s",
                exc,
            )
            return await asyncio.to_thread(self._grpc.validate_token, token)

    async def check_role(self, user_id: str, role: str) -> bool:
        if self._mode == "grpc":
            logger.debug("[AuthHybridClient] check_role via gRPC")
            return await asyncio.to_thread(self._grpc.check_role, user_id, role)

        if self._mode == "rabbit":
            logger.debug("[AuthHybridClient] check_role via RabbitMQ")
            return await self._rabbit.check_role(user_id, role)

        try:
            result = await self._rabbit.check_role(user_id, role)
            logger.debug("[AuthHybridClient] check_role via RabbitMQ OK")
            return result
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning(
                "[AuthHybridClient] Auth RabbitMQ RPC failed, falling back to gRPC: %s",
                exc,
            )
            return await asyncio.to_thread(self._grpc.check_role, user_id, role)

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        if self._mode == "grpc":
            logger.debug("[AuthHybridClient] get_user_by_id via gRPC")
            return await asyncio.to_thread(self._grpc.get_user_by_id, user_id)

        if self._mode == "rabbit":
            logger.debug("[AuthHybridClient] get_user_by_id via RabbitMQ")
            return await self._rabbit.get_user_by_id(user_id)

        try:
            result = await self._rabbit.get_user_by_id(user_id)
            logger.debug("[AuthHybridClient] get_user_by_id via RabbitMQ OK")
            return result
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning(
                "[AuthHybridClient] Auth RabbitMQ RPC failed, falling back to gRPC: %s",
                exc,
            )
            return await asyncio.to_thread(self._grpc.get_user_by_id, user_id)


auth_client = AuthHybridClient()
