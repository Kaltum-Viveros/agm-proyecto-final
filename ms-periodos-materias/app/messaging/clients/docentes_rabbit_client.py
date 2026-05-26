import logging
from typing import Any

from shared.agm_messaging.contracts import (
    RPC_DOCENTES_GET_DOCENTE_BY_ID,
    RPC_DOCENTES_GET_DOCENTE_BY_NOMBRE,
)
from shared.agm_messaging.exceptions import RPCException
from shared.agm_messaging.rpc_client import RabbitRpcClient

logger = logging.getLogger(__name__)


class DocentesRabbitClient:
    """Cliente RPC RabbitMQ hacia MS-3 Docentes-Alumnos para MS-2."""

    def __init__(self) -> None:
        self._client = RabbitRpcClient()

    async def verificar_docente(self, docente_id: str) -> bool:
        response = await self._client.call(
            RPC_DOCENTES_GET_DOCENTE_BY_ID,
            {"docente_id": str(docente_id)},
        )
        data = self._data_or_raise(response)
        logger.info("[DocentesRabbitClient] verificar_docente via RabbitMQ OK")
        return bool(data.get("found", False))

    async def resolver_docente_por_nombre(self, nombre_completo: str) -> str | None:
        response = await self._client.call(
            RPC_DOCENTES_GET_DOCENTE_BY_NOMBRE,
            {"nombre": nombre_completo},
        )
        data = self._data_or_raise(response)

        if data.get("found"):
            logger.info("[DocentesRabbitClient] resolver_docente_por_nombre via RabbitMQ OK")
            docente = data.get("docente") or {}
            return docente.get("docente_id") or None

        logger.info(
            "[DocentesRabbitClient] Business response resolver_docente_por_nombre: %s",
            data.get("error_code") or data.get("message"),
        )
        return None

    def _data_or_raise(self, response: dict[str, Any]) -> dict[str, Any]:
        if response.get("success"):
            return response.get("data") or {}
        raise RPCException(str(response.get("error") or "Docentes RPC error"))
