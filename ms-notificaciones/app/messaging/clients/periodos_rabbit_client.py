import logging
from typing import Any

from shared.agm_messaging.contracts import RPC_PERIODOS_GET_MATERIA_BY_ID
from shared.agm_messaging.rpc_client import RabbitRpcClient

logger = logging.getLogger(__name__)


class PeriodosRabbitClient:
    """Cliente RPC RabbitMQ hacia MS-2 Periodos & Materias para MS-6."""

    def __init__(self) -> None:
        self._client = RabbitRpcClient()

    async def obtener_materia(self, materia_id: str) -> dict[str, Any]:
        response = await self._client.call(
            RPC_PERIODOS_GET_MATERIA_BY_ID,
            {"materia_id": str(materia_id)},
        )
        data = self._data_or_empty(response)

        if data.get("found"):
            logger.info("[PeriodosRabbitClient] obtener_materia via RabbitMQ OK")
            materia = data.get("materia") or {}
            return {"nombre": materia.get("nombre") or "Materia Desconocida"}

        logger.info(
            "[PeriodosRabbitClient] Business response obtener_materia: %s",
            data.get("error_code") or data.get("message"),
        )
        return {"nombre": "Materia Desconocida"}

    def _data_or_empty(self, response: dict[str, Any]) -> dict[str, Any]:
        if response.get("success"):
            return response.get("data") or {}

        logger.error("[PeriodosRabbitClient] RPC Periodos error response: %s", response.get("error"))
        return {}
