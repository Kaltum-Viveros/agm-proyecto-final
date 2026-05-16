import grpc
import logging
from app.grpc.generated import notificaciones_pb2, notificaciones_pb2_grpc
from app.core.config import settings

class NotifClient:
    def __init__(self):
        self._channel = None
        self._stub = None

    def _get_stub(self):
        if self._stub is None:
            self._channel = grpc.insecure_channel(f"{settings.ms_notificaciones_grpc_host}:{settings.ms_notificaciones_grpc_port}")
            self._stub = notificaciones_pb2_grpc.NotificacionServiceStub(self._channel)
        return self._stub

    def enviar_cierre_materia(self, materia_id: str) -> bool:
        """
        Llama al MS-6 para enviar correos de cierre de actas a todos los alumnos de la materia.
        """
        stub = self._get_stub()
        if not stub:
            return False
        
        try:
            request = notificaciones_pb2.CierreMateriaRequest(
                materia_id=str(materia_id)
            )
            response = stub.SendCierreMateria(request)
            return response.success
        except Exception as e:
            logging.error(f"Error gRPC al llamar a CierreMateria en MS-6: {e}")
            return False

notif_client = NotifClient()
