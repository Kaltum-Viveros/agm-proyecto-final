import logging
from typing import Any

from shared.agm_messaging.contracts import (
    RPC_ASISTENCIAS_GET_ASISTENCIA_ALUMNO,
    RPC_ASISTENCIAS_GET_ASISTENCIAS_MATERIA,
    RPC_ASISTENCIAS_GET_ESTADISTICAS_ASISTENCIA,
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


class AsistenciasRabbitClient:
    """Cliente RPC RabbitMQ hacia MS-5 Asistencias para MS-7."""

    def __init__(self) -> None:
        self._client = RabbitRpcClient()

    async def get_asistencia_alumno(self, id_alumno: str, id_materia: str):
        response = await self._client.call(
            RPC_ASISTENCIAS_GET_ASISTENCIA_ALUMNO,
            {"alumno_id": str(id_alumno), "materia_id": str(id_materia)},
        )
        data = self._data_or_raise(response)
        print("[AsistenciasRabbitClient] get_asistencia_alumno via RabbitMQ OK", flush=True)

        if not data.get("found"):
            logger.info(
                "[AsistenciasRabbitClient] Business response get_asistencia_alumno: %s",
                data.get("error_code") or data.get("message"),
            )
            return None

        return ProtoLike(
            asistencias=[
                self._build_detalle(asistencia)
                for asistencia in data.get("asistencias", [])
            ],
            total_presentes=int(data.get("total_presentes") or 0),
            total_retardos=int(data.get("total_retardos") or 0),
        )

    async def get_asistencias_materia(self, id_materia: str):
        response = await self._client.call(
            RPC_ASISTENCIAS_GET_ASISTENCIAS_MATERIA,
            {"materia_id": str(id_materia)},
        )
        data = self._data_or_raise(response)
        print("[AsistenciasRabbitClient] get_asistencias_materia via RabbitMQ OK", flush=True)

        return ProtoLike(
            asistencias=[
                self._build_resumen(asistencia)
                for asistencia in data.get("asistencias", [])
            ]
        )

    async def get_estadisticas_asistencia(self, id_materia: str):
        response = await self._client.call(
            RPC_ASISTENCIAS_GET_ESTADISTICAS_ASISTENCIA,
            {"materia_id": str(id_materia)},
        )
        data = self._data_or_raise(response)
        print("[AsistenciasRabbitClient] get_estadisticas_asistencia via RabbitMQ OK", flush=True)

        if not data.get("found", True):
            logger.info(
                "[AsistenciasRabbitClient] Business response get_estadisticas_asistencia: %s",
                data.get("error_code") or data.get("message"),
            )
            return None

        return ProtoLike(
            total_alumnos=int(data.get("total_alumnos") or 0),
            porcentaje_asistencia_general=float(
                data.get("porcentaje_asistencia_general")
                or data.get("promedio_asistencia")
                or 0
            ),
            total_sesiones_impartidas=int(
                data.get("total_sesiones_impartidas")
                or data.get("total_sesiones")
                or 0
            ),
        )

    def _build_detalle(self, data: dict[str, Any]) -> ProtoLike:
        return ProtoLike(
            id_sesion=int(data.get("id_sesion") or data.get("sesion_id") or 0),
            estado=data.get("estado") or "",
            fecha_registro=data.get("fecha_registro") or data.get("fecha") or "",
        )

    def _build_resumen(self, data: dict[str, Any]) -> ProtoLike:
        return ProtoLike(
            id_alumno=data.get("id_alumno") or data.get("alumno_id") or "",
            total_presentes=int(data.get("total_presentes") or data.get("presentes") or 0),
            total_retardos=int(data.get("total_retardos") or data.get("retardos") or 0),
        )

    def _data_or_raise(self, response: dict[str, Any]) -> dict[str, Any]:
        if response.get("success"):
            return response.get("data") or {}
        raise RPCException(str(response.get("error") or "Asistencias RPC error"))
