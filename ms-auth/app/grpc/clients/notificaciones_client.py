import asyncio
import grpc
import os
import logging
from app.grpc.generated import notificaciones_pb2
from app.grpc.generated import notificaciones_pb2_grpc
from app.messaging.clients.notificaciones_event_client import notificaciones_event_client

class NotificacionesClient:
    def __init__(self):
        host = os.getenv("NOTIFICACIONES_GRPC_HOST", "ms-notificaciones")
        port = os.getenv("NOTIFICACIONES_GRPC_PORT", "50056")
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = notificaciones_pb2_grpc.NotificacionServiceStub(self.channel)

    def enviar_reset_password(self, usuario_id: str, email: str, reset_token: str) -> bool:
        mode = os.getenv("COMMUNICATION_MODE", "hybrid").lower()

        if mode != "grpc":
            try:
                asyncio.run(
                    notificaciones_event_client.publish_reset_password(
                        usuario_id=usuario_id,
                        email=email,
                        reset_token=reset_token,
                    )
                )
                return True
            except Exception as e:
                logging.warning(
                    "[NotificacionesEventClient] RabbitMQ event publish failed, "
                    "falling back to gRPC: %s",
                    e,
                )
                if mode == "rabbit":
                    return False

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
