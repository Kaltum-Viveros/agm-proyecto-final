import logging
from typing import Any

from shared.agm_messaging.contracts import (
    RPC_DOCENTES_GET_ALUMNO_BY_ID,
    RPC_DOCENTES_GET_ALUMNO_BY_EMAIL,
    RPC_DOCENTES_IS_ALUMNO_EN_MATERIA,
)
from shared.agm_messaging.exceptions import RPCException
from shared.agm_messaging.rpc_client import RabbitRpcClient

logger = logging.getLogger(__name__)


class DocentesRabbitClient:
    """Cliente RPC RabbitMQ hacia MS-3 Docentes-Alumnos para MS-4."""

    def __init__(self) -> None:
        self._client = RabbitRpcClient()

    async def is_alumno_en_materia(self, alumno_id: str, materia_id: str) -> bool:
        response = await self._client.call(
            RPC_DOCENTES_IS_ALUMNO_EN_MATERIA,
            {"alumno_id": str(alumno_id), "materia_id": str(materia_id)},
        )
        data = self._data_or_raise(response)
        logger.info("[DocentesRabbitClient] is_alumno_en_materia via RabbitMQ OK")
        return bool(data.get("enrolled", False))

    async def get_alumno_by_email(self, email: str) -> dict[str, Any] | None:
        response = await self._client.call(
            RPC_DOCENTES_GET_ALUMNO_BY_EMAIL,
            {"email": email.strip().lower()},
        )
        data = self._data_or_raise(response)

        if data.get("found"):
            logger.info("[DocentesRabbitClient] get_alumno_by_email via RabbitMQ OK")
            return self._adapt_alumno(data.get("alumno") or {})

        logger.info(
            "[DocentesRabbitClient] Business response get_alumno_by_email: %s",
            data.get("error_code") or data.get("message"),
        )
        return None

    async def get_alumno_perfil(self, alumno_id: str) -> dict[str, Any] | None:
        response = await self._client.call(
            RPC_DOCENTES_GET_ALUMNO_BY_ID,
            {"alumno_id": str(alumno_id)},
        )
        data = self._data_or_raise(response)

        if data.get("found"):
            logger.info("[DocentesRabbitClient] get_alumno_perfil via RabbitMQ OK")
            return self._adapt_alumno(data.get("alumno") or {})

        logger.info(
            "[DocentesRabbitClient] Business response get_alumno_perfil: %s",
            data.get("error_code") or data.get("message"),
        )
        return None

    def _adapt_alumno(self, alumno: dict[str, Any]) -> dict[str, Any]:
        return {
            "alumno_id": alumno.get("alumno_id") or "",
            "nombre_completo": alumno.get("nombre_completo") or "",
            "matricula": alumno.get("matricula") or "",
            "correo": alumno.get("correo") or alumno.get("email") or "",
        }

    def _data_or_raise(self, response: dict[str, Any]) -> dict[str, Any]:
        if response.get("success"):
            return response.get("data") or {}
        raise RPCException(str(response.get("error") or "Docentes RPC error"))
