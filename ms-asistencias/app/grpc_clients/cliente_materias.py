import logging

import grpc

from app.core.config import settings
from app.generated import periodos_materias_pb2, periodos_materias_pb2_grpc


class ClienteMaterias:
    def __init__(self):
        self.target = f"{settings.MATERIAS_GRPC_HOST}:{settings.MATERIAS_GRPC_PORT}"
        self.channel = grpc.aio.insecure_channel(self.target)
        self.stub = periodos_materias_pb2_grpc.PeriodosMateriasServiceStub(self.channel)

    async def verificar_materia_docente(self, id_materia: int, id_docente: int) -> bool:
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
            logging.error(f"Error gRPC al conectar con MS-2 (Materias): {e.details()}")
            # Si el servicio está caído, retornamos False por seguridad
            return False


cliente_materias = ClienteMaterias()
