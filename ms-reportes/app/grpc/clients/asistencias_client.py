"""
NOTA DE SEGURIDAD (canal gRPC):
  grpc.insecure_channel se utiliza unicamente porque este microservicio corre
  dentro de la red interna Docker/desarrollo, donde los canales entre contenedores
  son confiables. En un entorno de produccion real donde los servicios cruzan redes
  no confiables, se debe implementar TLS/mTLS.
"""
import grpc
from app.core.config import settings
from app.grpc.generated import asistencias_pb2, asistencias_pb2_grpc

class AsistenciasClient:
    def __init__(self):
        self.host = settings.ASISTENCIAS_GRPC_HOST
        self.port = settings.ASISTENCIAS_GRPC_PORT
        self.timeout = settings.GRPC_TIMEOUT_SECONDS

    def _get_stub(self, channel):
        return asistencias_pb2_grpc.AsistenciasServiceStub(channel)

    def get_asistencia_alumno(self, id_alumno: str, id_materia: str):
        with grpc.insecure_channel(f"{self.host}:{self.port}") as channel:
            stub = self._get_stub(channel)
            try:
                request = asistencias_pb2.AsistenciaAlumnoRequest(
                    id_alumno=str(id_alumno), 
                    id_materia=str(id_materia)
                )
                response = stub.GetAsistenciaAlumno(request, timeout=self.timeout)
                return response
            except grpc.RpcError as e:
                print(f"[gRPC MS-5] GetAsistenciaAlumno error: {e.code()} - {e.details()}")
                return None

    def get_asistencias_materia(self, id_materia: str):
        with grpc.insecure_channel(f"{self.host}:{self.port}") as channel:
            stub = self._get_stub(channel)
            try:
                request = asistencias_pb2.AsistenciasMateriaRequest(
                    id_materia=str(id_materia)
                )
                response = stub.GetAsistenciasMateria(request, timeout=self.timeout)
                return response
            except grpc.RpcError as e:
                print(f"[gRPC MS-5] GetAsistenciasMateria error: {e.code()} - {e.details()}")
                return None

    def get_estadisticas_asistencia(self, id_materia: str):
        with grpc.insecure_channel(f"{self.host}:{self.port}") as channel:
            stub = self._get_stub(channel)
            try:
                request = asistencias_pb2.EstadisticasRequest(id_materia=str(id_materia))
                response = stub.GetEstadisticasAsistencia(request, timeout=self.timeout)
                return response
            except grpc.RpcError as e:
                print(f"[gRPC MS-5] GetEstadisticasAsistencia error: {e.code()} - {e.details()}")
                return None

asistencias_client = AsistenciasClient()

