"""
NOTA DE SEGURIDAD (canal gRPC):
  grpc.insecure_channel se utiliza unicamente porque este microservicio corre
  dentro de la red interna Docker/desarrollo, donde los canales entre contenedores
  son confiables. En un entorno de produccion real donde los servicios cruzan redes
  no confiables, se debe implementar TLS/mTLS.
"""
import grpc
from app.core.config import settings
from app.grpc.generated import docentes_alumnos_pb2, docentes_alumnos_pb2_grpc

class DocentesAlumnosClient:
    def __init__(self):
        self.host = settings.DOCENTES_ALUMNOS_GRPC_HOST
        self.port = settings.DOCENTES_ALUMNOS_GRPC_PORT
        self.timeout = settings.GRPC_TIMEOUT_SECONDS

    def _get_stub(self, channel):
        return docentes_alumnos_pb2_grpc.DocentesAlumnosServiceStub(channel)

    def get_alumnos_by_materia(self, materia_id: str):
        with grpc.insecure_channel(f"{self.host}:{self.port}") as channel:
            stub = self._get_stub(channel)
            request = docentes_alumnos_pb2.GetAlumnosRequest(materia_id=materia_id)
            try:
                response = stub.GetAlumnosByMateria(request, timeout=self.timeout)
                return response
            except grpc.RpcError as e:
                print(f"[gRPC MS-3] GetAlumnosByMateria error: {e.code()} - {e.details()}")
                return None

    def get_alumno_by_id(self, alumno_id: str):
        with grpc.insecure_channel(f"{self.host}:{self.port}") as channel:
            stub = self._get_stub(channel)
            request = docentes_alumnos_pb2.AlumnoIdRequest(alumno_id=alumno_id)
            try:
                response = stub.GetAlumnoById(request, timeout=self.timeout)
                return response
            except grpc.RpcError as e:
                print(f"[gRPC MS-3] GetAlumnoById error: {e.code()} - {e.details()}")
                return None

    def get_materias_by_alumno(self, alumno_id: str):
        with grpc.insecure_channel(f"{self.host}:{self.port}") as channel:
            stub = self._get_stub(channel)
            request = docentes_alumnos_pb2.AlumnoIdRequest(alumno_id=alumno_id)
            try:
                response = stub.GetMateriasByAlumno(request, timeout=self.timeout)
                return response
            except grpc.RpcError as e:
                print(f"[gRPC MS-3] GetMateriasByAlumno error: {e.code()} - {e.details()}")
                return None

docentes_alumnos_client = DocentesAlumnosClient()

