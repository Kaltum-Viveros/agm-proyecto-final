import logging
from typing import Any

from shared.agm_messaging.contracts import (
    RPC_CALIFICACIONES_GET_CONCENTRADO,
    RPC_CALIFICACIONES_GET_ESTADISTICAS_MATERIA,
    RPC_CALIFICACIONES_GET_PROMEDIO_ALUMNO,
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


class CalificacionesRabbitClient:
    """Cliente RPC RabbitMQ hacia MS-4 Calificaciones para MS-7."""

    def __init__(self) -> None:
        self._client = RabbitRpcClient()

    async def get_concentrado(self, materia_id: str, modo: str = "actual"):
        response = await self._client.call(
            RPC_CALIFICACIONES_GET_CONCENTRADO,
            {"materia_id": str(materia_id), "modo": modo},
        )
        data = self._data_or_raise(response)
        print("[CalificacionesRabbitClient] get_concentrado via RabbitMQ OK", flush=True)

        if not data.get("found"):
            logger.info(
                "[CalificacionesRabbitClient] Business response get_concentrado: %s",
                data.get("error_code") or data.get("message"),
            )
            return None

        return ProtoLike(
            materia_id=data.get("materia_id") or str(materia_id),
            modo=data.get("modo") or modo,
            total_alumnos=int(data.get("total_alumnos") or data.get("total") or 0),
            ponderaciones=[
                self._build_ponderacion(ponderacion)
                for ponderacion in data.get("ponderaciones", [])
            ],
            alumnos=[
                self._build_alumno(alumno)
                for alumno in data.get("alumnos") or data.get("concentrado") or []
            ],
        )

    async def get_promedio_alumno(
        self,
        alumno_id: str,
        materia_id: str | None = None,
        modo: str = "actual",
    ):
        payload = {"alumno_id": str(alumno_id), "modo": modo}
        if materia_id:
            payload["materia_id"] = str(materia_id)

        response = await self._client.call(
            RPC_CALIFICACIONES_GET_PROMEDIO_ALUMNO,
            payload,
        )
        data = self._data_or_raise(response)
        print("[CalificacionesRabbitClient] get_promedio_alumno via RabbitMQ OK", flush=True)

        if not data.get("found"):
            logger.info(
                "[CalificacionesRabbitClient] Business response get_promedio_alumno: %s",
                data.get("error_code") or data.get("message"),
            )
            return None

        return ProtoLike(
            alumno_id=data.get("alumno_id") or str(alumno_id),
            materia_id=data.get("materia_id") or str(materia_id or ""),
            modo=data.get("modo") or modo,
            peso_considerado=float(data.get("peso_considerado", 0) or 0),
            promedio_real=float(data.get("promedio_real") or data.get("promedio") or 0),
            promedio_redondeado=int(data.get("promedio_redondeado") or round(float(data.get("promedio") or 0))),
            detalle_ponderaciones=[
                self._build_detalle(detalle)
                for detalle in data.get("detalle_ponderaciones", [])
            ],
        )

    async def get_estadisticas_materia(self, materia_id: str, modo: str = "actual"):
        response = await self._client.call(
            RPC_CALIFICACIONES_GET_ESTADISTICAS_MATERIA,
            {"materia_id": str(materia_id), "modo": modo},
        )
        data = self._data_or_raise(response)
        print("[CalificacionesRabbitClient] get_estadisticas_materia via RabbitMQ OK", flush=True)

        if not data.get("found"):
            logger.info(
                "[CalificacionesRabbitClient] Business response get_estadisticas_materia: %s",
                data.get("error_code") or data.get("message"),
            )
            return None

        return ProtoLike(
            materia_id=data.get("materia_id") or str(materia_id),
            modo=data.get("modo") or modo,
            total_alumnos=int(data.get("total_alumnos") or 0),
            promedio_grupal=float(data.get("promedio_grupal") or data.get("promedio") or 0),
            aprobados=int(data.get("aprobados") or 0),
            reprobados=int(data.get("reprobados") or 0),
            promedio_minimo=float(data.get("promedio_minimo") or 0),
            promedio_maximo=float(data.get("promedio_maximo") or 0),
        )

    def _build_ponderacion(self, data: dict[str, Any]) -> ProtoLike:
        return ProtoLike(
            id=data.get("id") or "",
            materia_id=data.get("materia_id") or "",
            nombre=data.get("nombre") or "",
            porcentaje=float(data.get("porcentaje") or 0),
            orden=int(data.get("orden") or 0),
        )

    def _build_alumno(self, data: dict[str, Any]) -> ProtoLike:
        return ProtoLike(
            alumno_id=data.get("alumno_id") or "",
            modo=data.get("modo") or "actual",
            peso_considerado=float(data.get("peso_considerado") or 0),
            promedio_real=float(data.get("promedio_real") or data.get("calificacion_final") or 0),
            promedio_redondeado=int(data.get("promedio_redondeado") or data.get("calificacion_final") or 0),
            detalle_ponderaciones=[
                self._build_detalle(detalle)
                for detalle in data.get("detalle_ponderaciones", [])
            ],
        )

    def _build_detalle(self, data: dict[str, Any]) -> ProtoLike:
        return ProtoLike(
            ponderacion_id=data.get("ponderacion_id") or "",
            nombre=data.get("nombre") or "",
            porcentaje=float(data.get("porcentaje") or 0),
            total_actividades=int(data.get("total_actividades") or 0),
            actividades_calificadas=int(data.get("actividades_calificadas") or 0),
            promedio_criterio=float(data.get("promedio_criterio") or 0),
            aporte=float(data.get("aporte") or 0),
            incluida_en_calculo=bool(data.get("incluida_en_calculo", False)),
        )

    def _data_or_raise(self, response: dict[str, Any]) -> dict[str, Any]:
        if response.get("success"):
            return response.get("data") or {}
        raise RPCException(str(response.get("error") or "Calificaciones RPC error"))
