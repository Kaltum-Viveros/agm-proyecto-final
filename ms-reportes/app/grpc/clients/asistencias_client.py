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

    def get_asistencia_alumno(self, id_alumno: str | int, id_materia: str | int):
        """
        NOTA IMPORTANTE: El proto actual de MS-5 requiere int32 para los IDs.
        Si la aplicación usa UUIDs (strings), esto fallará hasta que se
        resuelva el contrato o se haga un mapeo de IDs.
        """
        with grpc.insecure_channel(f"{self.host}:{self.port}") as channel:
            stub = self._get_stub(channel)
            try:
                # Convertimos a int() temporalmente, asumiendo que puedan ser numéricos
                # o el proto cambiará en el futuro.
                request = asistencias_pb2.AsistenciaAlumnoRequest(
                    id_alumno=int(id_alumno), 
                    id_materia=int(id_materia)
                )
                response = stub.GetAsistenciaAlumno(request, timeout=self.timeout)
                return response
            except ValueError:
                print("[gRPC MS-5] Error: id_alumno o id_materia no es convertible a int32 (¿es un UUID?)")
                return None
            except grpc.RpcError as e:
                print(f"[gRPC MS-5] GetAsistenciaAlumno error: {e.code()} - {e.details()}")
                return None

    def get_estadisticas_asistencia(self, id_materia: str | int):
        with grpc.insecure_channel(f"{self.host}:{self.port}") as channel:
            stub = self._get_stub(channel)
            try:
                request = asistencias_pb2.EstadisticasRequest(id_materia=int(id_materia))
                response = stub.GetEstadisticasAsistencia(request, timeout=self.timeout)
                return response
            except ValueError:
                print("[gRPC MS-5] Error: id_materia no es convertible a int32 (¿es un UUID?)")
                return None
            except grpc.RpcError as e:
                print(f"[gRPC MS-5] GetEstadisticasAsistencia error: {e.code()} - {e.details()}")
                return None

asistencias_client = AsistenciasClient()
