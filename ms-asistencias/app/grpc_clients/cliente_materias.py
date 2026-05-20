import logging

import grpc

from app.core.config import settings
from app.generated import periodos_materias_pb2, periodos_materias_pb2_grpc


class ClienteMaterias:
    def __init__(self):
        self.target = f"{settings.MATERIAS_GRPC_HOST}:{settings.MATERIAS_GRPC_PORT}"
        self._channel = None
        self._stub = None
        self._loop = None

    @property
    def stub(self):
        import asyncio
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None

        if self._channel is None or self._loop != current_loop:
            self._loop = current_loop
            self._channel = grpc.aio.insecure_channel(self.target)
            self._stub = periodos_materias_pb2_grpc.PeriodosMateriasServiceStub(self._channel)
        return self._stub

    async def verificar_materia_docente(self, id_materia: str, id_docente: str) -> bool:
        """
        Consulta al MS-2 si la materia existe y si realmente es impartida por este docente.
        """
        try:
            request = periodos_materias_pb2.GetMateriaByIdRequest(materia_id=str(id_materia))
            response = await self.stub.GetMateriaById(request)
            
            # Verificamos si la respuesta contiene un docente_id que coincida
            if response and response.docente_id == str(id_docente):
                return True
            return False
        except grpc.RpcError as e:
            logging.error(f"Error gRPC al conectar con MS-2 (Materias): {e.details() if hasattr(e, 'details') else e}")
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="El servicio de materias no está disponible actualmente."
            )


cliente_materias = ClienteMaterias()
