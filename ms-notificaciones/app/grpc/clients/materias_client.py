import grpc
import logging
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'generated')))

try:
    from app.grpc.generated import periodos_materias_pb2, periodos_materias_pb2_grpc
except ImportError:
    pass

from app.core.config import settings

class MateriasClient:
    def __init__(self):
        self._channel = None
        self._stub = None

    def _get_stub(self):
        if self._stub is None:
            host = settings.ms_periodos_materias_grpc_host
            port = settings.ms_periodos_materias_grpc_port
            self._channel = grpc.insecure_channel(f"{host}:{port}")
            if 'periodos_materias_pb2_grpc' in globals():
                self._stub = periodos_materias_pb2_grpc.PeriodosMateriasServiceStub(self._channel)
        return self._stub

    def obtener_materia(self, materia_id: str) -> dict:
        """
        Llama al MS-2 para obtener los datos de una materia.
        """
        stub = self._get_stub()
        if not stub:
            return {"nombre": "Materia Prueba (Mock)"}
        try:
            request = periodos_materias_pb2.GetMateriaByIdRequest(materia_id=str(materia_id))
            response = stub.GetMateriaById(request)
            return {"nombre": response.materia.nombre}
        except Exception as e:
            logging.error(f"Error gRPC al consultar MS-2: {e}")
            return {"nombre": "Materia Desconocida"}

materias_client = MateriasClient()
