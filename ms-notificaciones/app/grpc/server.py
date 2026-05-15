import grpc
from concurrent import futures
import logging
import sys
import os

# Fix para el problema clásico de imports en Python gRPC
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'generated')))

try:
    # Estos módulos se generarán desde el archivo proto compartido
    from app.grpc.generated import notificaciones_pb2
    from app.grpc.generated import notificaciones_pb2_grpc
except ImportError:
    pass

from app.core.database import SessionLocal
from app.services import notificacion_service
from app.schemas.notificacion_schema import (
    BienvenidaRequest, 
    BajaMateriaRequest, 
    CierreMateriaRequest,
    ResetPasswordRequest
)

class NotificacionServiceServicer(notificaciones_pb2_grpc.NotificacionServiceServicer if 'notificaciones_pb2_grpc' in globals() else object):
    
    def _get_db(self):
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def SendBienvenida(self, request, context):
        try:
            db = next(self._get_db())
            # Tomamos los strings directamente (UUIDs)
            data = BienvenidaRequest(
                alumno_id=request.alumno_id,
                materia_id=request.materia_id if request.materia_id else "",
                password_temporal=request.password_temporal
            )
            notificacion_service.procesar_bienvenida(db, data)
            return notificaciones_pb2.NotifResponse(success=True, message="Notificación de bienvenida procesada")
        except Exception as e:
            logging.error(f"Error en SendBienvenida: {e}")
            return notificaciones_pb2.NotifResponse(success=False, message=str(e))

    def SendBajaNotif(self, request, context):
        try:
            db = next(self._get_db())
            data = BajaMateriaRequest(
                alumno_id=request.alumno_id,
                docente_id=request.docente_id,
                materia_id=request.materia_id
            )
            notificacion_service.procesar_baja(db, data)
            return notificaciones_pb2.NotifResponse(success=True, message="Notificación de baja procesada")
        except Exception as e:
            logging.error(f"Error en SendBajaNotif: {e}")
            return notificaciones_pb2.NotifResponse(success=False, message=str(e))

    def SendCierreMateria(self, request, context):
        try:
            db = next(self._get_db())
            data = CierreMateriaRequest(materia_id=request.materia_id)
            notificacion_service.procesar_cierre_materia(db, data)
            return notificaciones_pb2.NotifResponse(success=True, message="Notificación de cierre de actas procesada")
        except Exception as e:
            logging.error(f"Error en SendCierreMateria: {e}")
            return notificaciones_pb2.NotifResponse(success=False, message=str(e))

    def SendResetPassword(self, request, context):
        try:
            db = next(self._get_db())
            data = ResetPasswordRequest(
                usuario_id=request.usuario_id,
                email=request.email,
                reset_token=request.reset_token
            )
            notificacion_service.procesar_reset_password(db, data)
            return notificaciones_pb2.NotifResponse(success=True, message="Notificación de reseteo de contraseña enviada")
        except Exception as e:
            logging.error(f"Error en SendResetPassword: {e}")
            return notificaciones_pb2.NotifResponse(success=False, message=str(e))


def serve():
    if 'notificaciones_pb2_grpc' not in globals():
        print("Error: Los archivos .proto no han sido compilados. Por favor compila el archivo notificaciones.proto primero.")
        return

    port = "50056"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    notificaciones_pb2_grpc.add_NotificacionServiceServicer_to_server(NotificacionServiceServicer(), server)
    server.add_insecure_port(f'[::]:{port}')
    print(f"Servidor gRPC iniciado y escuchando en el puerto {port}...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()
