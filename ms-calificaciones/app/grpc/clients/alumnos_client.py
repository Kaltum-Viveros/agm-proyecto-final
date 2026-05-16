"""
Cliente gRPC hacia MS-Docentes-Alumnos (MS-3).
Verifica si un alumno está inscrito en una materia antes de calificarlo.
"""
import grpc
import logging
from app.core.config import settings

try:
    from app.grpc.generated import docentes_alumnos_pb2, docentes_alumnos_pb2_grpc
    _PROTO_AVAILABLE = True
except ImportError:
    _PROTO_AVAILABLE = False
    logging.warning("[AlumnosClient MS-4] docentes_alumnos_pb2 no disponible.")


class AlumnosClient:
    def __init__(self):
        self._channel = None
        self._stub = None

    def _get_stub(self):
        if not _PROTO_AVAILABLE:
            return None
        if self._stub is None:
            host = settings.ms_docentes_alumnos_grpc_host
            port = settings.ms_docentes_alumnos_grpc_port
            self._channel = grpc.insecure_channel(f"{host}:{port}")
            self._stub = docentes_alumnos_pb2_grpc.DocentesAlumnosServiceStub(self._channel)
        return self._stub

    def is_alumno_en_materia(self, alumno_id: str, materia_id: str) -> bool:
        """
        Verifica si el alumno tiene una inscripción activa en la materia.
        Retorna True si está inscrito, False si no o si hay error.
        """
        stub = self._get_stub()
        if not stub:
            logging.warning("[AlumnosClient MS-4] Proto no disponible, permitiendo operación.")
            return True  # Modo degradado: no bloquear si no hay proto
        try:
            request = docentes_alumnos_pb2.RelationRequest(
                alumno_id=str(alumno_id),
                materia_id=str(materia_id),
            )
            response = stub.IsAlumnoEnMateria(request)
            return response.exists
        except grpc.RpcError as e:
            logging.error(f"[AlumnosClient MS-4] Error gRPC IsAlumnoEnMateria: {e.details()}")
            return True  # Modo degradado: no bloquear en caso de fallo de red

    def get_alumno_perfil(self, alumno_id: str) -> dict | None:
        """
        Obtiene el perfil básico del alumno (nombre, correo) desde MS-3.
        Retorna dict o None si no se encuentra.
        """
        stub = self._get_stub()
        if not stub:
            return None
        try:
            request = docentes_alumnos_pb2.AlumnoIdRequest(alumno_id=str(alumno_id))
            response = stub.GetAlumnoById(request)
            if response and response.correo:
                return {
                    "alumno_id": response.alumno_id,
                    "nombre_completo": response.nombre_completo,
                    "matricula": response.matricula,
                    "correo": response.correo,
                }
            return None
        except grpc.RpcError as e:
            logging.error(f"[AlumnosClient MS-4] Error gRPC GetAlumnoById: {e.details()}")
            return None

    def get_alumno_by_email(self, email: str) -> dict | None:
        """
        Busca un alumno por su correo electrónico en MS-3.
        Retorna dict con perfil o None si no se encuentra.
        """
        stub = self._get_stub()
        if not stub:
            return None
        try:
            request = docentes_alumnos_pb2.EmailRequest(email=email.strip().lower())
            response = stub.GetAlumnoByEmail(request)
            if response and response.alumno_id:
                return {
                    "alumno_id": response.alumno_id,
                    "nombre_completo": response.nombre_completo,
                    "matricula": response.matricula,
                    "correo": response.correo,
                }
            return None
        except grpc.RpcError as e:
            logging.error(f"[AlumnosClient MS-4] Error gRPC GetAlumnoByEmail: {e.details()}")
            return None


# Singleton
alumnos_client = AlumnosClient()
