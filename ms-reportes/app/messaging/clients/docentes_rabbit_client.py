import logging
from typing import Any

from shared.agm_messaging.contracts import (
    RPC_DOCENTES_GET_ALUMNO_BY_ID,
    RPC_DOCENTES_GET_ALUMNOS_BY_MATERIA,
    RPC_DOCENTES_GET_MATERIAS_BY_ALUMNO,
)
from shared.agm_messaging.exceptions import RPCException
from shared.agm_messaging.rpc_client import RabbitRpcClient

logger = logging.getLogger(__name__)


class ProtoLike:
    """Objeto liviano con atributos para compatibilidad con protobuf."""

    def __init__(self, **kwargs) -> None:
        self.__dict__.update(kwargs)

    def HasField(self, name: str) -> bool:
        return getattr(self, name, None) is not None


class DocentesRabbitClient:
    """Cliente RPC RabbitMQ hacia MS-3 Docentes-Alumnos para MS-7."""

    def __init__(self) -> None:
        self._client = RabbitRpcClient()

    async def get_alumnos_by_materia(self, materia_id: str):
        response = await self._client.call(
            RPC_DOCENTES_GET_ALUMNOS_BY_MATERIA,
            {"materia_id": str(materia_id)},
        )
        data = self._data_or_raise(response)
        logger.info("[DocentesRabbitClient] get_alumnos_by_materia via RabbitMQ OK")
        return ProtoLike(
            alumnos=[
                self._build_alumno(alumno)
                for alumno in data.get("alumnos", [])
            ]
        )

    async def get_alumno_by_id(self, alumno_id: str):
        response = await self._client.call(
            RPC_DOCENTES_GET_ALUMNO_BY_ID,
            {"alumno_id": str(alumno_id)},
        )
        data = self._data_or_raise(response)

        if data.get("found"):
            logger.info("[DocentesRabbitClient] get_alumno_by_id via RabbitMQ OK")
            return self._build_alumno(data.get("alumno") or {})

        logger.info(
            "[DocentesRabbitClient] Business response get_alumno_by_id: %s",
            data.get("error_code") or data.get("message"),
        )
        return None

    async def get_materias_by_alumno(self, alumno_id: str):
        response = await self._client.call(
            RPC_DOCENTES_GET_MATERIAS_BY_ALUMNO,
            {"alumno_id": str(alumno_id)},
        )
        data = self._data_or_raise(response)
        logger.info("[DocentesRabbitClient] get_materias_by_alumno via RabbitMQ OK")
        return ProtoLike(
            materias_ids=[
                materia.get("materia_id") or materia.get("materia_ofertada_id") or ""
                for materia in data.get("materias", [])
                if materia.get("materia_id") or materia.get("materia_ofertada_id")
            ]
        )

    def _build_alumno(self, data: dict[str, Any]) -> ProtoLike:
        return ProtoLike(
            alumno_id=data.get("alumno_id") or "",
            user_id=data.get("user_id") or "",
            nombre_completo=data.get("nombre_completo") or "",
            matricula=data.get("matricula") or "",
            correo=data.get("correo") or data.get("email") or "",
            email=data.get("email") or data.get("correo") or "",
            activo=bool(data.get("activo", True)),
        )

    def _data_or_raise(self, response: dict[str, Any]) -> dict[str, Any]:
        if response.get("success"):
            return response.get("data") or {}
        raise RPCException(str(response.get("error") or "Docentes RPC error"))
