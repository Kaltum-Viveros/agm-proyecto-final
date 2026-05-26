import logging
from typing import Any

from shared.agm_messaging.contracts import (
    RPC_DOCENTES_GET_ALUMNO_BY_EMAIL,
    RPC_DOCENTES_GET_ALUMNOS_BY_MATERIA,
    RPC_DOCENTES_GET_DOCENTE_BY_EMAIL,
    RPC_DOCENTES_IS_ALUMNO_EN_MATERIA,
)
from shared.agm_messaging.exceptions import RPCException
from shared.agm_messaging.rpc_client import RabbitRpcClient

logger = logging.getLogger(__name__)


class DocentesRabbitClient:
    """Cliente RPC RabbitMQ hacia MS-3 Docentes-Alumnos para MS-5."""

    def __init__(self) -> None:
        self._client = RabbitRpcClient()

    async def verificar_alumno_en_materia(self, id_alumno: str, id_materia: str) -> bool:
        response = await self._client.call(
            RPC_DOCENTES_IS_ALUMNO_EN_MATERIA,
            {"alumno_id": str(id_alumno), "materia_id": str(id_materia)},
        )
        data = self._data_or_raise(response)
        logger.info("[DocentesRabbitClient] verificar_alumno_en_materia via RabbitMQ OK")
        return bool(data.get("enrolled", False))

    async def obtener_alumnos_por_materia(self, id_materia: str) -> list[dict[str, Any]]:
        response = await self._client.call(
            RPC_DOCENTES_GET_ALUMNOS_BY_MATERIA,
            {"materia_id": str(id_materia)},
        )
        data = self._data_or_raise(response)
        logger.info("[DocentesRabbitClient] obtener_alumnos_por_materia via RabbitMQ OK")
        return [
            {
                "id_alumno": alumno.get("alumno_id") or "",
                "matricula": alumno.get("matricula") or "",
                "nombre_completo": alumno.get("nombre_completo") or "",
            }
            for alumno in data.get("alumnos", [])
        ]

    async def obtener_docente_por_email(self, email: str) -> dict[str, Any] | None:
        response = await self._client.call(
            RPC_DOCENTES_GET_DOCENTE_BY_EMAIL,
            {"email": email},
        )
        data = self._data_or_raise(response)

        if data.get("found"):
            logger.info("[DocentesRabbitClient] obtener_docente_por_email via RabbitMQ OK")
            docente = data.get("docente") or {}
            return {
                "docente_id": docente.get("docente_id") or "",
                "nombre_completo": docente.get("nombre_completo") or "",
                "correo": docente.get("correo") or docente.get("email") or "",
            }

        logger.info(
            "[DocentesRabbitClient] Business response obtener_docente_por_email: %s",
            data.get("error_code") or data.get("message"),
        )
        return None

    async def obtener_alumno_por_email(self, email: str) -> dict[str, Any] | None:
        response = await self._client.call(
            RPC_DOCENTES_GET_ALUMNO_BY_EMAIL,
            {"email": email},
        )
        data = self._data_or_raise(response)

        if data.get("found"):
            logger.info("[DocentesRabbitClient] obtener_alumno_por_email via RabbitMQ OK")
            alumno = data.get("alumno") or {}
            return {
                "alumno_id": alumno.get("alumno_id") or "",
                "nombre_completo": alumno.get("nombre_completo") or "",
                "matricula": alumno.get("matricula") or "",
                "correo": alumno.get("correo") or alumno.get("email") or "",
            }

        logger.info(
            "[DocentesRabbitClient] Business response obtener_alumno_por_email: %s",
            data.get("error_code") or data.get("message"),
        )
        return None

    def _data_or_raise(self, response: dict[str, Any]) -> dict[str, Any]:
        if response.get("success"):
            return response.get("data") or {}
        raise RPCException(str(response.get("error") or "Docentes RPC error"))
