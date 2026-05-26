import asyncio
import logging
import os
from typing import Any

import aio_pika.exceptions
import aiormq.exceptions

from app.grpc.clients.ms2_client import MS2Client
from app.messaging.clients.periodos_rabbit_client import PeriodosRabbitClient
from shared.agm_messaging.exceptions import RPCException, RPCTimeoutException

logger = logging.getLogger(__name__)

_TRANSPORT_EXCEPTIONS = (
    TimeoutError,
    ConnectionError,
    OSError,
    RuntimeError,
    RPCException,
    RPCTimeoutException,
    aio_pika.exceptions.AMQPException,
    aiormq.exceptions.AMQPError,
)


class PeriodosHybridClient:
    """RabbitMQ primero y fallback gRPC hacia MS-2 para MS-3."""

    def __init__(self) -> None:
        self._rabbit = PeriodosRabbitClient()
        self._grpc = MS2Client()
        self._mode = os.getenv("COMMUNICATION_MODE", "hybrid").lower()
        logger.info("[PeriodosHybridClient] COMMUNICATION_MODE=%s", self._mode)

    async def get_materia_by_nrc(self, nrc: str) -> dict[str, Any] | None:
        if self._mode == "grpc":
            return await asyncio.to_thread(self._grpc_get_materia_by_nrc, nrc)

        if self._mode == "rabbit":
            return await self._rabbit.get_materia_by_nrc(nrc)

        try:
            return await self._rabbit.get_materia_by_nrc(nrc)
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning(
                "[PeriodosHybridClient] RabbitMQ RPC failed, falling back to gRPC: %s",
                exc,
            )
            return await asyncio.to_thread(self._grpc_get_materia_by_nrc, nrc)

    async def obtener_materia_y_periodo(self, docente_id: str, nrc_pdf: str):
        materia = await self.get_materia_by_nrc(nrc_pdf)
        if not materia:
            return None, None, None

        return (
            materia.get("materia_id") or materia.get("materia_ofertada_id"),
            materia.get("periodo_id") or (materia.get("periodo") or {}).get("periodo_id"),
            materia.get("seccion"),
        )

    def _grpc_get_materia_by_nrc(self, nrc: str) -> dict[str, Any] | None:
        materia_id, periodo_id, seccion = self._grpc.obtener_materia_y_periodo("", nrc)
        if not materia_id:
            return None

        return {
            "materia_id": materia_id,
            "materia_ofertada_id": materia_id,
            "periodo_id": periodo_id,
            "seccion": seccion,
        }


periodos_client = PeriodosHybridClient()
