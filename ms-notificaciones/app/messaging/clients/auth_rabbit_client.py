import logging
from typing import Any, Dict, Optional

from shared.agm_messaging.contracts import (
    RPC_AUTH_CHECK_ROLE,
    RPC_AUTH_CREATE_PASSWORD_RESET_TOKEN,
    RPC_AUTH_GET_USER_BY_ID,
    RPC_AUTH_VALIDATE_TOKEN,
)
from shared.agm_messaging.rpc_client import RabbitRpcClient

logger = logging.getLogger(__name__)


class AuthRabbitClient:
    """Cliente RPC RabbitMQ hacia MS-Auth con respuestas compatibles con MS-6."""

    def __init__(self) -> None:
        self._client = RabbitRpcClient()

    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        response = await self._client.call(RPC_AUTH_VALIDATE_TOKEN, {"token": token})
        data = self._data_or_empty(response)
        claims = data.get("claims") or {}

        if data.get("valid"):
            logger.debug("[AuthRabbitClient] validate_token via RabbitMQ OK")
            return {
                "valid": True,
                "user_id": claims.get("user_id"),
                "email": claims.get("email"),
                "role": claims.get("role"),
                "activo": claims.get("activo"),
            }

        logger.info(
            "[AuthRabbitClient] Auth business response validate_token: %s",
            data.get("error_code") or data.get("message"),
        )
        return {
            "valid": False,
            "error": data.get("message") or self._error_message(response),
        }

    async def check_role(self, user_id: str, role: str) -> bool:
        response = await self._client.call(
            RPC_AUTH_CHECK_ROLE,
            {"user_id": str(user_id), "role": role},
        )
        data = self._data_or_empty(response)
        allowed = bool(data.get("allowed", False))
        if allowed:
            logger.debug("[AuthRabbitClient] check_role via RabbitMQ OK")
        else:
            logger.info(
                "[AuthRabbitClient] Auth business response check_role: %s",
                data.get("error_code") or data.get("message"),
            )
        return allowed

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        response = await self._client.call(
            RPC_AUTH_GET_USER_BY_ID,
            {"user_id": str(user_id)},
        )
        data = self._data_or_empty(response)
        if data.get("found"):
            logger.debug("[AuthRabbitClient] get_user_by_id via RabbitMQ OK")
            return data.get("user")

        logger.info(
            "[AuthRabbitClient] Auth business response get_user_by_id: %s",
            data.get("error_code") or data.get("message"),
        )
        return None

    async def create_password_reset_token(self, email: str) -> Optional[Dict[str, Any]]:
        response = await self._client.call(
            RPC_AUTH_CREATE_PASSWORD_RESET_TOKEN,
            {"email": str(email)},
        )
        data = self._data_or_empty(response)

        if data.get("success") and data.get("token"):
            logger.info("[AuthRabbitClient] create_password_reset_token via RabbitMQ OK")
            return {
                "user_id": data.get("user_id"),
                "email": data.get("email") or email,
                "token": data.get("token"),
                "expires_at": data.get("expires_at"),
            }

        logger.info(
            "[AuthRabbitClient] Auth business response create_password_reset_token: %s",
            data.get("error_code") or data.get("message"),
        )
        return None

    def _data_or_empty(self, response: dict) -> dict:
        if response.get("success"):
            return response.get("data") or {}

        logger.error("[AuthRabbitClient] RPC Auth error response: %s", response.get("error"))
        return {}

    def _error_message(self, response: dict) -> str:
        error = response.get("error") or {}
        return str(error.get("message") or "Error en RabbitMQ RPC Auth")
