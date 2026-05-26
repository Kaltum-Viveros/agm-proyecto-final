import logging
from typing import Any

from shared.agm_messaging.contracts import (
    RPC_PERIODOS_GET_MATERIA_BY_ID,
    RPC_PERIODOS_GET_MATERIAS_BY_DOCENTE,
    RPC_PERIODOS_GET_PERIODO_ACTIVO,
)
from shared.agm_messaging.rpc_client import RabbitRpcClient

logger = logging.getLogger(__name__)


class ProtoLike:
    """Objeto liviano con atributos y HasField para compatibilidad con protobuf."""

    def __init__(self, **kwargs) -> None:
        self.__dict__.update(kwargs)

    def HasField(self, name: str) -> bool:
        return getattr(self, name, None) is not None


class PeriodosRabbitClient:
    """Cliente RPC RabbitMQ hacia MS-2 Periodos & Materias para MS-7."""

    def __init__(self) -> None:
        self._client = RabbitRpcClient()

    async def get_materia_by_id(self, materia_id: str):
        response = await self._client.call(
            RPC_PERIODOS_GET_MATERIA_BY_ID,
            {"materia_id": str(materia_id)},
        )
        data = self._data_or_empty(response)

        if data.get("found"):
            logger.info("[PeriodosRabbitClient] get_materia_by_id via RabbitMQ OK")
            return self._build_materia(data.get("materia") or {})

        logger.info(
            "[PeriodosRabbitClient] Business response get_materia_by_id: %s",
            data.get("error_code") or data.get("message"),
        )
        return None

    async def get_materias_by_docente(self, docente_id: str):
        response = await self._client.call(
            RPC_PERIODOS_GET_MATERIAS_BY_DOCENTE,
            {"docente_id": str(docente_id)},
        )
        data = self._data_or_empty(response)
        logger.info("[PeriodosRabbitClient] get_materias_by_docente via RabbitMQ OK")
        return ProtoLike(
            materias=[
                self._build_materia(materia)
                for materia in data.get("materias", [])
            ]
        )

    async def get_periodo_activo(self):
        response = await self._client.call(RPC_PERIODOS_GET_PERIODO_ACTIVO, {})
        data = self._data_or_empty(response)

        if data.get("found"):
            logger.info("[PeriodosRabbitClient] get_periodo_activo via RabbitMQ OK")
            return self._build_periodo(data.get("periodo") or {})

        logger.info(
            "[PeriodosRabbitClient] Business response get_periodo_activo: %s",
            data.get("error_code") or data.get("message"),
        )
        return None

    def _build_materia(self, data: dict[str, Any]) -> ProtoLike:
        materia_catalogo = data.get("materia") or {}
        periodo = data.get("periodo") or {}
        return ProtoLike(
            materia_ofertada_id=data.get("materia_ofertada_id") or data.get("materia_id") or "",
            nrc=data.get("nrc") or "",
            seccion=data.get("seccion") or "",
            estado=data.get("estado") or "",
            periodo=self._build_periodo(periodo) if periodo else None,
            materia=ProtoLike(
                materia_catalogo_id=materia_catalogo.get("materia_catalogo_id") or data.get("materia_catalogo_id") or "",
                clave=materia_catalogo.get("clave") or data.get("clave") or "",
                nombre=materia_catalogo.get("nombre") or data.get("nombre") or "",
            ),
            docente_id=data.get("docente_id") or "",
            docente_nombre=data.get("docente_nombre") or "",
            horarios=[
                ProtoLike(**horario)
                for horario in data.get("horarios", [])
            ],
        )

    def _build_periodo(self, data: dict[str, Any]) -> ProtoLike:
        return ProtoLike(
            periodo_id=data.get("periodo_id") or "",
            nombre=data.get("nombre") or "",
            fecha_inicio=data.get("fecha_inicio") or "",
            fecha_fin=data.get("fecha_fin") or "",
            activo=bool(data.get("activo", False)),
        )

    def _data_or_empty(self, response: dict[str, Any]) -> dict[str, Any]:
        if response.get("success"):
            return response.get("data") or {}

        logger.error("[PeriodosRabbitClient] RPC Periodos error response: %s", response.get("error"))
        return {}
