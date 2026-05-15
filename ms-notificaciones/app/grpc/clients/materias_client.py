import grpc
import logging
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'generated')))

try:
    from app.grpc.generated import periodos_materias_pb2, periodos_materias_pb2_grpc
except ImportError:
    pass

class MateriasClient:
    def __init__(self, host: str = "ms-periodos-materias", port: int = 50052):
        self.host = host
        self.port = port
        self.channel = None
        self.stub = None

    def _connect(self):
        if not self.channel:
            self.channel = grpc.insecure_channel(f"{self.host}:{self.port}")
            if 'periodos_materias_pb2_grpc' in globals():
                self.stub = periodos_materias_pb2_grpc.PeriodosMateriasServiceStub(self.channel)

    def obtener_materia(self, materia_id: int) -> dict:
        """
        Llama al MS-2 para obtener los datos de una materia.
        """
        self._connect()
        try:
            if not self.stub:
                return {"nombre": "Materia Prueba (Mock)"}

            request = periodos_materias_pb2.GetMateriaByIdRequest(materia_id=str(materia_id))
            response = self.stub.GetMateriaById(request)
            return {"nombre": response.materia.nombre}
        except Exception as e:
            logging.error(f"Error gRPC al consultar MS-2: {e}")
            return {"nombre": "Materia Desconocida"}

materias_client = MateriasClient()
