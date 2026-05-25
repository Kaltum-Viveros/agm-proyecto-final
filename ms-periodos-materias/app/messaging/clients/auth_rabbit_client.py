import logging
from typing import Dict, Any, Optional

from shared.agm_messaging.rpc_client import RabbitRpcClient
from shared.agm_messaging.contracts import (
    RPC_AUTH_VALIDATE_TOKEN,
    RPC_AUTH_GET_USER_BY_ID,
    RPC_AUTH_CHECK_ROLE,
    RPC_AUTH_CREATE_OR_GET_USER_IDENTITY
)

logger = logging.getLogger(__name__)

class AuthRabbitClient:
    """Cliente RPC por RabbitMQ hacia MS-Auth."""

    def __init__(self):
        self._client = RabbitRpcClient()

    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Llama al MS-Auth por RabbitMQ RPC para validar el token.
        Retorna la estructura idéntica a la que devolvía el AuthClient (gRPC).
        Lanza excepciones de transporte si hay errores de red.
        """
        payload = {"token": token}
        response = await self._client.call(RPC_AUTH_VALIDATE_TOKEN, payload)
        
        if response.get("success"):
            data = response.get("data", {})
            return {
                "valid": data.get("valid", False),
                "user_id": data.get("claims", {}).get("user_id"),
                "email": data.get("claims", {}).get("email"),
                "role": data.get("claims", {}).get("role"),
                "activo": data.get("claims", {}).get("activo"),
            }
        else:
            return {
                "valid": False, 
                "error": response.get("error", {}).get("message", "Error desconocido en RabbitMQ")
            }

    async def check_role(self, user_id: str, role: str) -> bool:
        """
        Llama a MS-Auth por RabbitMQ RPC para validar el rol.
        """
        payload = {"user_id": user_id, "role": role}
        response = await self._client.call(RPC_AUTH_CHECK_ROLE, payload)
        
        if response.get("success"):
            return response.get("data", {}).get("allowed", False)
        return False

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información de usuario por ID usando RabbitMQ RPC.
        """
        payload = {"user_id": str(user_id)}
        response = await self._client.call(RPC_AUTH_GET_USER_BY_ID, payload)
        
        if response.get("success"):
            data = response.get("data", {})
            if data.get("found"):
                return data.get("user")
            return None
        return None
