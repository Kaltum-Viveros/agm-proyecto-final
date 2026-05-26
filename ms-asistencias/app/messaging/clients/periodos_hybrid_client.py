import logging
import os

import aio_pika.exceptions
import aiormq.exceptions
import grpc
from fastapi import HTTPException, status

from app.core.config import settings
from app.generated import periodos_materias_pb2, periodos_materias_pb2_grpc
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
    """RabbitMQ primero y fallback gRPC hacia MS-2 para MS-5."""

    def __init__(self) -> None:
        self._rabbit = PeriodosRabbitClient()
        self._grpc_target = f"{settings.MATERIAS_GRPC_HOST}:{settings.MATERIAS_GRPC_PORT}"
        self._mode = os.getenv("COMMUNICATION_MODE", "hybrid").lower()
        logger.info("[PeriodosHybridClient] COMMUNICATION_MODE=%s", self._mode)

    async def verificar_materia_docente(self, id_materia: str, id_docente: str) -> bool:
        if self._mode == "grpc":
            return await self._grpc_verificar_materia_docente(id_materia, id_docente)

        if self._mode == "rabbit":
            return await self._rabbit.verificar_materia_docente(id_materia, id_docente)

        try:
            return await self._rabbit.verificar_materia_docente(id_materia, id_docente)
        except _TRANSPORT_EXCEPTIONS as exc:
            logger.warning(
                "[PeriodosHybridClient] RabbitMQ RPC failed, falling back to gRPC: %s",
                exc,
            )
            return await self._grpc_verificar_materia_docente(id_materia, id_docente)

    async def _grpc_verificar_materia_docente(self, id_materia: str, id_docente: str) -> bool:
        try:
            async with grpc.aio.insecure_channel(self._grpc_target) as channel:
                stub = periodos_materias_pb2_grpc.PeriodosMateriasServiceStub(channel)
                response = await stub.GetMateriaById(
                    periodos_materias_pb2.GetMateriaByIdRequest(materia_id=str(id_materia))
                )
                return bool(response and response.docente_id == str(id_docente))
        except grpc.aio.AioRpcError as exc:
            if exc.code() in (grpc.StatusCode.NOT_FOUND, grpc.StatusCode.INVALID_ARGUMENT):
                return False
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="El servicio de materias no esta disponible actualmente.",
            )


periodos_client = PeriodosHybridClient()
