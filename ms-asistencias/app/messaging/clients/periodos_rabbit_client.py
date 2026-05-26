import logging
from typing import Any

from shared.agm_messaging.contracts import RPC_PERIODOS_GET_MATERIA_BY_ID
from shared.agm_messaging.rpc_client import RabbitRpcClient

logger = logging.getLogger(__name__)


class PeriodosRabbitClient:
    """Cliente RPC RabbitMQ hacia MS-2 Periodos & Materias para MS-5."""

    def __init__(self) -> None:
        self._client = RabbitRpcClient()

    async def get_materia_by_id(self, materia_id: str) -> dict[str, Any] | None:
        response = await self._client.call(
            RPC_PERIODOS_GET_MATERIA_BY_ID,
            {"materia_id": str(materia_id)},
        )
        data = self._data_or_empty(response)

        if data.get("found"):
            logger.info("[PeriodosRabbitClient] get_materia_by_id via RabbitMQ OK")
            return data.get("materia")

        logger.info(
            "[PeriodosRabbitClient] Business response get_materia_by_id: %s",
            data.get("error_code") or data.get("message"),
        )
        return None

    async def verificar_materia_docente(self, id_materia: str, id_docente: str) -> bool:
        materia = await self.get_materia_by_id(id_materia)
        return bool(materia and materia.get("docente_id") == str(id_docente))

    def _data_or_empty(self, response: dict[str, Any]) -> dict[str, Any]:
        if response.get("success"):
            return response.get("data") or {}

        logger.error("[PeriodosRabbitClient] RPC Periodos error response: %s", response.get("error"))
        return {}
