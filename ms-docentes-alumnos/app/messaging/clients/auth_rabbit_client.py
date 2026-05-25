import logging
from typing import Tuple

from app.grpc.generated import auth_pb2
from shared.agm_messaging.contracts import (
    RPC_AUTH_CHECK_ROLE,
    RPC_AUTH_CREATE_OR_GET_USER_IDENTITY,
    RPC_AUTH_GET_USER_BY_ID,
    RPC_AUTH_VALIDATE_TOKEN,
)
from shared.agm_messaging.rpc_client import RabbitRpcClient

logger = logging.getLogger(__name__)


class AuthRabbitClient:
    """Cliente RPC RabbitMQ hacia MS-Auth con respuestas compatibles con MS-3."""

    def __init__(self) -> None:
        self._client = RabbitRpcClient()

    async def validate_token(self, token: str):
        response = await self._client.call(RPC_AUTH_VALIDATE_TOKEN, {"token": token})
        data = self._data_or_empty(response)
        claims = data.get("claims") or {}

        return auth_pb2.ValidateTokenResponse(
            valid=bool(data.get("valid", False)),
            claims=auth_pb2.UserClaims(
                user_id=str(claims.get("user_id", "")),
                email=str(claims.get("email", "")),
                role=str(claims.get("role", "")),
                jti=str(claims.get("jti", "")),
                activo=bool(claims.get("activo", False)),
            ),
            error_code=str(data.get("error_code", "")),
            message=str(data.get("message") or self._error_message(response)),
        )

    async def get_user_by_id(self, user_id: str):
        response = await self._client.call(
            RPC_AUTH_GET_USER_BY_ID,
            {"user_id": str(user_id)},
        )
        data = self._data_or_empty(response)
        if not data.get("found"):
            return None
        return self._build_user_profile(data.get("user") or {})

    async def check_role(self, user_id: str, role: str) -> bool:
        response = await self._client.call(
            RPC_AUTH_CHECK_ROLE,
            {"user_id": str(user_id), "role": role},
        )
        data = self._data_or_empty(response)
        return bool(data.get("allowed", False))

    async def create_or_get_user_identity(
        self,
        nombre: str,
        email: str,
        role: str = "Alumno",
    ) -> Tuple[str | None, str | None]:
        response = await self._client.call(
            RPC_AUTH_CREATE_OR_GET_USER_IDENTITY,
            {
                "nombre_completo": nombre,
                "email": email,
                "role": role,
            },
        )
        data = self._data_or_empty(response)
        user = data.get("user") or {}
        user_id = user.get("user_id")
        if data.get("created") or user_id:
            return user_id, data.get("temporary_password") or None
        return None, None

    def _data_or_empty(self, response: dict) -> dict:
        if response.get("success"):
            return response.get("data") or {}
        logger.error("[AuthRabbitClient] RPC Auth error: %s", response.get("error"))
        return {}

    def _error_message(self, response: dict) -> str:
        error = response.get("error") or {}
        return str(error.get("message") or "Error en RabbitMQ RPC Auth")

    def _build_user_profile(self, user: dict):
        return auth_pb2.UserProfile(
            user_id=str(user.get("user_id", "")),
            nombre_completo=str(user.get("nombre_completo", "")),
            email=str(user.get("email", "")),
            role=str(user.get("role", "")),
            activo=bool(user.get("activo", False)),
        )
