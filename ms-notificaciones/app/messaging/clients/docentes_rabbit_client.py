import logging
from typing import Any

from shared.agm_messaging.contracts import (
    RPC_DOCENTES_GET_ALUMNO_BY_ID,
    RPC_DOCENTES_GET_ALUMNOS_BY_MATERIA,
    RPC_DOCENTES_GET_DOCENTE_BY_ID,
)
from shared.agm_messaging.exceptions import RPCException
from shared.agm_messaging.rpc_client import RabbitRpcClient

logger = logging.getLogger(__name__)


class DocentesRabbitClient:
    """Cliente RPC RabbitMQ hacia MS-3 Docentes-Alumnos para MS-6."""

    def __init__(self) -> None:
        self._client = RabbitRpcClient()

    async def obtener_alumno(self, alumno_id: str) -> dict[str, Any]:
        response = await self._client.call(
            RPC_DOCENTES_GET_ALUMNO_BY_ID,
            {"alumno_id": str(alumno_id)},
        )
        data = self._data_or_raise(response)

        if data.get("found"):
            logger.info("[DocentesRabbitClient] obtener_alumno via RabbitMQ OK")
            alumno = data.get("alumno") or {}
            return {
                "email": alumno.get("email") or alumno.get("correo") or "",
                "correo": alumno.get("correo") or alumno.get("email") or "",
                "nombre": alumno.get("nombre_completo") or "",
            }

        logger.info(
            "[DocentesRabbitClient] Business response obtener_alumno: %s",
            data.get("error_code") or data.get("message"),
        )
        return {"email": "", "correo": "", "nombre": ""}

    async def obtener_docente(self, docente_id: str) -> dict[str, Any]:
        response = await self._client.call(
            RPC_DOCENTES_GET_DOCENTE_BY_ID,
            {"docente_id": str(docente_id)},
        )
        data = self._data_or_raise(response)

        if data.get("found"):
            logger.info("[DocentesRabbitClient] obtener_docente via RabbitMQ OK")
            docente = data.get("docente") or {}
            return {
                "email": docente.get("email") or docente.get("correo") or "",
                "correo": docente.get("correo") or docente.get("email") or "",
                "nombre": docente.get("nombre_completo") or "",
            }

        logger.info(
            "[DocentesRabbitClient] Business response obtener_docente: %s",
            data.get("error_code") or data.get("message"),
        )
        return {"email": "", "correo": "", "nombre": ""}

    async def obtener_alumnos_por_materia(self, materia_id: str) -> list[dict[str, Any]]:
        response = await self._client.call(
            RPC_DOCENTES_GET_ALUMNOS_BY_MATERIA,
            {"materia_id": str(materia_id)},
        )
        data = self._data_or_raise(response)
        logger.info("[DocentesRabbitClient] obtener_alumnos_por_materia via RabbitMQ OK")
        return [
            {
                "email": alumno.get("email") or alumno.get("correo") or "",
                "correo": alumno.get("correo") or alumno.get("email") or "",
                "nombre": alumno.get("nombre_completo") or "",
            }
            for alumno in data.get("alumnos", [])
        ]

    def _data_or_raise(self, response: dict[str, Any]) -> dict[str, Any]:
        if response.get("success"):
            return response.get("data") or {}
        raise RPCException(str(response.get("error") or "Docentes RPC error"))
