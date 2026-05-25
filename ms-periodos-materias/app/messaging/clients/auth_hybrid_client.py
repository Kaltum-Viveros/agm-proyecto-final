"""
Cliente híbrido de Auth para MS-2.
Intenta RabbitMQ primero; hace fallback a gRPC solo en errores de transporte.
"""
import asyncio
import logging
import os
from typing import Dict, Any, Optional

from app.grpc.clients.auth_client import AuthClient
from app.messaging.clients.auth_rabbit_client import AuthRabbitClient
import aio_pika.exceptions
import aiormq.exceptions
from shared.agm_messaging.exceptions import RPCException, RPCTimeoutException

logger = logging.getLogger(__name__)

# Excepciones que representan fallos de TRANSPORTE (se hace fallback).
# Errores de negocio (token inválido, etc.) NO entran aquí — se respetan.
_TRANSPORT_EXCEPTIONS = (
    RPCException, 
    RPCTimeoutException, 
    ConnectionError, 
    OSError, 
    RuntimeError, 
    TimeoutError,
    aio_pika.exceptions.AMQPException,
    aiormq.exceptions.AMQPError
)


class AuthHybridClient:
    """
    Fachada que enruta llamadas Auth a RabbitMQ o gRPC según COMMUNICATION_MODE.

    grpc   → solo gRPC (sin RabbitMQ).
    rabbit → solo RabbitMQ (sin gRPC).
    hybrid → RabbitMQ primero; fallback a gRPC solo en errores de transporte.
    """

    def __init__(self) -> None:
        self._rabbit = AuthRabbitClient()
        self._grpc = AuthClient()
        self._mode = os.getenv("COMMUNICATION_MODE", "grpc").lower()
        logger.info("[AuthHybridClient] COMMUNICATION_MODE=%s", self._mode)

    # ------------------------------------------------------------------
    # validate_token
    # ------------------------------------------------------------------
    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        if self._mode == "grpc":
            logger.debug("[AuthHybridClient] validate_token → gRPC")
            return await asyncio.to_thread(self._grpc.validate_token, token)

        if self._mode == "rabbit":
            logger.debug("[AuthHybridClient] validate_token → RabbitMQ")
            return await self._rabbit.validate_token(token)

        # hybrid
        try:
            result = await self._rabbit.validate_token(token)
            logger.debug("[AuthHybridClient] validate_token → RabbitMQ OK")
            return result
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning(
                "[AuthHybridClient] Auth RabbitMQ RPC failed, falling back to gRPC: %s", exc
            )
            return await asyncio.to_thread(self._grpc.validate_token, token)

    # ------------------------------------------------------------------
    # check_role
    # ------------------------------------------------------------------
    async def check_role(self, user_id: str, role: str) -> bool:
        if self._mode == "grpc":
            logger.debug("[AuthHybridClient] check_role → gRPC")
            return await asyncio.to_thread(self._grpc.check_role, user_id, role)

        if self._mode == "rabbit":
            logger.debug("[AuthHybridClient] check_role → RabbitMQ")
            return await self._rabbit.check_role(user_id, role)

        # hybrid
        try:
            result = await self._rabbit.check_role(user_id, role)
            logger.debug("[AuthHybridClient] check_role → RabbitMQ OK")
            return result
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning(
                "[AuthHybridClient] Auth RabbitMQ RPC failed, falling back to gRPC: %s", exc
            )
            return await asyncio.to_thread(self._grpc.check_role, user_id, role)

    # ------------------------------------------------------------------
    # get_user_by_id
    # ------------------------------------------------------------------
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        if self._mode == "grpc":
            logger.debug("[AuthHybridClient] get_user_by_id → gRPC (no implementado en gRPC client)")
            return None

        if self._mode == "rabbit":
            logger.debug("[AuthHybridClient] get_user_by_id → RabbitMQ")
            return await self._rabbit.get_user_by_id(user_id)

        # hybrid
        try:
            result = await self._rabbit.get_user_by_id(user_id)
            logger.debug("[AuthHybridClient] get_user_by_id → RabbitMQ OK")
            return result
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning(
                "[AuthHybridClient] Auth RabbitMQ RPC failed, falling back to gRPC: %s", exc
            )
            # gRPC client no expone get_user_by_id en MS-2; devolvemos None
            return None


# Singleton compartido — se importa desde deps.py
auth_client = AuthHybridClient()
