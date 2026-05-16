import grpc
import logging
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'generated')))

try:
    from app.grpc.generated import docentes_alumnos_pb2, docentes_alumnos_pb2_grpc
except ImportError:
    pass

from app.core.config import settings

class AlumnosClient:
    def __init__(self):
        self._channel = None
        self._stub = None

    def _get_stub(self):
        if self._stub is None:
            host = settings.ms_docentes_alumnos_grpc_host
            port = settings.ms_docentes_alumnos_grpc_port
            self._channel = grpc.insecure_channel(f"{host}:{port}")
            if 'docentes_alumnos_pb2_grpc' in globals():
                self._stub = docentes_alumnos_pb2_grpc.DocentesAlumnosServiceStub(self._channel)
        return self._stub

    def obtener_alumno(self, alumno_id: str) -> dict:
        """
        Llama al ms-docentes-alumnos para obtener el perfil detallado del alumno.
        """
        stub = self._get_stub()
        if not stub:
            return {"email": "correo_por_defecto@ejemplo.com", "nombre": "MOCK (Falta compilar protos)"}
        try:
            request = docentes_alumnos_pb2.AlumnoIdRequest(alumno_id=str(alumno_id))
            response = stub.GetAlumnoById(request)
            correo = response.correo if response.correo else "correo_por_defecto@ejemplo.com"
            return {"email": correo, "nombre": response.nombre_completo}
        except Exception as e:
            logging.error(f"Error gRPC al consultar alumno MS-3: {e}")
            return {"email": "error@ejemplo.com", "nombre": "Desconocido"}

    def obtener_docente(self, docente_id: str) -> dict:
        """
        Llama al ms-docentes-alumnos para obtener el perfil detallado del docente.
        """
        stub = self._get_stub()
        if not stub:
            return {"email": "correo_por_defecto@ejemplo.com", "nombre": "MOCK (Falta compilar protos)"}
        try:
            request = docentes_alumnos_pb2.DocenteIdRequest(docente_id=str(docente_id))
            response = stub.GetDocenteById(request)
            correo = response.correo if response.correo else "correo_por_defecto@ejemplo.com"
            return {"email": correo, "nombre": response.nombre_completo}
        except Exception as e:
            logging.error(f"Error gRPC al consultar docente MS-3: {e}")
            return {"email": "error@ejemplo.com", "nombre": "Desconocido"}

    def obtener_alumnos_por_materia(self, materia_id: str) -> list:
        """
        Obtiene la lista de perfiles de alumnos inscritos en una materia.
        """
        stub = self._get_stub()
        if not stub:
            return []
        try:
            request = docentes_alumnos_pb2.GetAlumnosRequest(materia_id=str(materia_id))
            response = stub.GetAlumnosByMateria(request)
            return [{"email": a.correo if a.correo else "correo_por_defecto@ejemplo.com", "nombre": a.nombre_completo} for a in response.alumnos]
        except Exception as e:
            logging.error(f"Error gRPC al consultar alumnos por materia MS-3: {e}")
            return []

alumnos_client = AlumnosClient()
