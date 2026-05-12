import grpc
from uuid import UUID

from app.core.config import settings

# TODO: Descomentar las siguientes líneas cuando el MS-3 esté implementado
# y los archivos generados .proto existan.
# from app.grpc.generated import alumnos_pb2, alumnos_pb2_grpc

class AlumnosGrpcClient:
    def __init__(self, host: str | None = None):
        self.host = host or settings.ms_alumnos_grpc_url

    def is_alumno_en_materia(self, alumno_id: UUID, materia_id: UUID) -> bool:
        """
        Llama al método IsAlumnoEnMateria del MS-3 de forma síncrona.
        
        Si el MS-3 no está listo, retorna True por defecto.
        """
        # TODO: Descomentar la implementación real cuando MS-3 esté disponible.
        # with grpc.insecure_channel(self.host) as channel:
        #     stub = alumnos_pb2_grpc.AlumnosServiceStub(channel)
        #     
        #     request = alumnos_pb2.IsAlumnoEnMateriaRequest(
        #         alumno_id=str(alumno_id),
        #         materia_id=str(materia_id)
        #     )
        #     
        #     try:
        #         # Usamos timeout de 5 segundos para que no bloquee por siempre
        #         response = stub.IsAlumnoEnMateria(request, timeout=5.0)
        #         return response.is_inscrito
        #     except grpc.RpcError as e:
        #         # Podríamos loguear el error aquí
        #         print(f"Error gRPC MS-3 (IsAlumnoEnMateria): {e.code()} - {e.details()}")
        #         return False
        
        # Simulación temporal (siempre válida)
        return True
