"""
NOTA DE SEGURIDAD (canal gRPC):
  grpc.insecure_channel se utiliza unicamente porque este microservicio corre
  dentro de la red interna Docker/desarrollo, donde los canales entre contenedores
  son confiables. En un entorno de produccion real donde los servicios cruzan redes
  no confiables, se debe implementar TLS/mTLS.
"""
import grpc
from app.core.config import settings
from app.grpc.generated import periodos_materias_pb2, periodos_materias_pb2_grpc

class PeriodosMateriasClient:
    def __init__(self):
        self.host = settings.PERIODOS_MATERIAS_GRPC_HOST
        self.port = settings.PERIODOS_MATERIAS_GRPC_PORT
        self.timeout = settings.GRPC_TIMEOUT_SECONDS

    def _get_stub(self, channel):
        return periodos_materias_pb2_grpc.PeriodosMateriasServiceStub(channel)

    def get_materia_by_id(self, materia_id: str):
        with grpc.insecure_channel(f"{self.host}:{self.port}") as channel:
            stub = self._get_stub(channel)
            request = periodos_materias_pb2.GetMateriaByIdRequest(materia_id=materia_id)
            try:
                response = stub.GetMateriaById(request, timeout=self.timeout)
                return response
            except grpc.RpcError as e:
                print(f"[gRPC MS-2] GetMateriaById error: {e.code()} - {e.details()}")
                return None

    def get_materias_by_docente(self, docente_id: str):
        with grpc.insecure_channel(f"{self.host}:{self.port}") as channel:
            stub = self._get_stub(channel)
            request = periodos_materias_pb2.GetMateriasByDocenteRequest(docente_id=docente_id)
            try:
                response = stub.GetMateriasByDocente(request, timeout=self.timeout)
                return response
            except grpc.RpcError as e:
                print(f"[gRPC MS-2] GetMateriasByDocente error: {e.code()} - {e.details()}")
                return None

    def get_periodo_activo(self):
        with grpc.insecure_channel(f"{self.host}:{self.port}") as channel:
            stub = self._get_stub(channel)
            request = periodos_materias_pb2.GetPeriodoActivoRequest()
            try:
                response = stub.GetPeriodoActivo(request, timeout=self.timeout)
                return response
            except grpc.RpcError as e:
                print(f"[gRPC MS-2] GetPeriodoActivo error: {e.code()} - {e.details()}")
                return None

periodos_materias_client = PeriodosMateriasClient()

