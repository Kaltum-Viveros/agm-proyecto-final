import grpc
import os
import logging
from app.grpc.generated import notificaciones_pb2
from app.grpc.generated import notificaciones_pb2_grpc

class NotificacionesClient:
    def __init__(self):
        host = os.getenv("NOTIFICACIONES_GRPC_HOST", "ms-notificaciones")
        port = os.getenv("NOTIFICACIONES_GRPC_PORT", "50056")
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = notificaciones_pb2_grpc.NotificacionServiceStub(self.channel)

    def enviar_reset_password(self, usuario_id: str, email: str, reset_token: str) -> bool:
        try:
            request = notificaciones_pb2.ResetPasswordRequest(
                usuario_id=usuario_id,
                email=email,
                reset_token=reset_token
            )
            response = self.stub.SendResetPassword(request, timeout=5)
            if not response.success:
                logging.error(f"Fallo al enviar notificación de reset: {response.message}")
            return response.success
        except grpc.RpcError as e:
            logging.error(f"Error gRPC al contactar ms-notificaciones: {e.details()}")
            return False

notificaciones_client = NotificacionesClient()
