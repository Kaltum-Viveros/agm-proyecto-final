import grpc
import os
from app.grpc.generated import notificaciones_pb2, notificaciones_pb2_grpc

class NotifClient:
    def __init__(self):
        self.host = os.getenv("MS6_HOST", "ms-notificaciones")
        self.port = os.getenv("MS6_PORT", "50056")
        self.channel = grpc.insecure_channel(f"{self.host}:{self.port}")
        self.stub = notificaciones_pb2_grpc.NotificacionServiceStub(self.channel)

    def enviar_bienvenida(self, nombre: str, correo: str, password: str, nrc: str):
        """Dispara el correo al MS-6 con las credenciales del alumno"""
        try:
            request = notificaciones_pb2.BienvenidaRequest(
                nombre_alumno=nombre,
                correo_alumno=correo,
                password_temporal=password,
                nrc_materia=nrc
            )
            response = self.stub.SendBienvenida(request)
            return response.success
        except Exception as e:
            print(f"Error gRPC MS-6: {e}")
            return False