import grpc
import logging
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'generated')))

try:
    from app.grpc.generated import docentes_alumnos_pb2, docentes_alumnos_pb2_grpc
except ImportError:
    pass

class AlumnosClient:
    def __init__(self, host: str = "ms-docentes-alumnos", port: int = 50051):
        self.host = host
        self.port = port
        self.channel = None
        self.stub = None

    def _connect(self):
        if not self.channel:
            self.channel = grpc.insecure_channel(f"{self.host}:{self.port}")
            if 'docentes_alumnos_pb2_grpc' in globals():
                self.stub = docentes_alumnos_pb2_grpc.DocentesAlumnosServiceStub(self.channel)

    def obtener_alumno(self, alumno_id: int) -> dict:
        """
        Llama al ms-docentes-alumnos para obtener el perfil detallado.
        """
        self._connect()
        try:
            if not self.stub:
                return {"email": "rinava404@gmail.com", "nombre": "MOCK (Falta compilar protos)"}
            
            request = docentes_alumnos_pb2.AlumnoIdRequest(alumno_id=str(alumno_id))
            response = self.stub.GetAlumnoById(request)
            
            # Si el correo de respuesta está vacío, usamos un default de seguridad para que no falle el SMTP
            correo = response.correo if response.correo else "correo_por_defecto@ejemplo.com"
            return {"email": correo, "nombre": response.nombre_completo}
        except Exception as e:
            logging.error(f"Error gRPC al consultar MS-3: {e}")
            return {"email": "error@ejemplo.com", "nombre": "Desconocido"}

alumnos_client = AlumnosClient()
