import grpc
from app.core.config import settings
from app.grpc.generated import calificaciones_pb2, calificaciones_pb2_grpc

class CalificacionesClient:
    def __init__(self):
        self.host = settings.CALIFICACIONES_GRPC_HOST
        self.port = settings.CALIFICACIONES_GRPC_PORT
        self.timeout = settings.GRPC_TIMEOUT_SECONDS

    def _get_stub(self, channel):
        return calificaciones_pb2_grpc.CalificacionesServiceStub(channel)

    def get_concentrado(self, materia_id: str, modo: str = "actual"):
        with grpc.insecure_channel(f"{self.host}:{self.port}") as channel:
            stub = self._get_stub(channel)
            request = calificaciones_pb2.GetConcentradoRequest(materia_id=materia_id, modo=modo)
            try:
                response = stub.GetConcentrado(request, timeout=self.timeout)
                return response
            except grpc.RpcError as e:
                print(f"[gRPC MS-4] GetConcentrado error: {e.code()} - {e.details()}")
                return None

    def get_promedio_alumno(self, alumno_id: str, materia_id: str, modo: str = "actual"):
        with grpc.insecure_channel(f"{self.host}:{self.port}") as channel:
            stub = self._get_stub(channel)
            request = calificaciones_pb2.GetPromedioAlumnoRequest(
                alumno_id=alumno_id, 
                materia_id=materia_id, 
                modo=modo
            )
            try:
                response = stub.GetPromedioAlumno(request, timeout=self.timeout)
                return response
            except grpc.RpcError as e:
                print(f"[gRPC MS-4] GetPromedioAlumno error: {e.code()} - {e.details()}")
                return None

    def get_estadisticas_materia(self, materia_id: str, modo: str = "actual"):
        with grpc.insecure_channel(f"{self.host}:{self.port}") as channel:
            stub = self._get_stub(channel)
            request = calificaciones_pb2.GetEstadisticasMateriaRequest(
                materia_id=materia_id, 
                modo=modo
            )
            try:
                response = stub.GetEstadisticasMateria(request, timeout=self.timeout)
                return response
            except grpc.RpcError as e:
                print(f"[gRPC MS-4] GetEstadisticasMateria error: {e.code()} - {e.details()}")
                return None

calificaciones_client = CalificacionesClient()
