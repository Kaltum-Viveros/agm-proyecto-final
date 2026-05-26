"""
Cliente gRPC hacia MS-1 Auth & Users para MS-7 Reportes & Estadísticas.
Valida tokens JWT presentados en endpoints REST.

NOTA DE SEGURIDAD (canal gRPC):
  grpc.insecure_channel se utiliza únicamente porque este microservicio corre
  dentro de la red interna Docker/desarrollo, donde los canales entre contenedores
  son confiables. En un entorno de producción real donde los servicios cruzan redes
  no confiables, se debe implementar TLS/mTLS.
"""
import logging
import grpc

from app.core.config import settings
from app.grpc.generated import auth_pb2, auth_pb2_grpc

logger = logging.getLogger(__name__)


class AuthClient:
    """Cliente gRPC hacia MS-1 (Auth & Users) para validar tokens JWT."""

    def __init__(self):
        self.host = settings.AUTH_GRPC_HOST
        self.port = settings.AUTH_GRPC_PORT
        self.timeout = settings.GRPC_TIMEOUT_SECONDS

    def _channel_target(self) -> str:
        return f"{self.host}:{self.port}"

    def validate_token(self, token: str) -> dict:
        """
        Valida el token JWT llamando a ValidateToken en MS-1.

        Retorna:
            dict con claims del usuario si el token es válido:
            {
                "valid": True,
                "user_id": str,
                "email": str,
                "role": str,
                "jti": str,
                "activo": bool,
            }

        Lanza:
            grpc.RpcError si MS-1 no está disponible (traducir a HTTP 503 en la capa API).
            ValueError si el token fue rechazado por MS-1 (traducir a HTTP 401 en la capa API).
        """
        with grpc.insecure_channel(self._channel_target()) as channel:
            stub = auth_pb2_grpc.AuthServiceStub(channel)
            request = auth_pb2.ValidateTokenRequest(token=token)
            try:
                response = stub.ValidateToken(request, timeout=self.timeout)
            except grpc.RpcError as e:
                logger.error(
                    f"[AuthClient MS-7] Error gRPC al validar token: "
                    f"code={e.code()} detail={e.details()}"
                )
                # Re-lanzar para que la dependencia FastAPI lo traduzca a HTTP 503
                raise

            if not response.valid:
                msg = response.message or "Token inválido o expirado"
                raise ValueError(msg)

            claims = response.claims
            return {
                "valid": True,
                "user_id": claims.user_id,
                "email": claims.email,
                "role": claims.role,
                "jti": claims.jti,
                "activo": claims.activo,
            }

    def check_role(self, user_id: str, role: str) -> bool:
        """Verifica el rol de un usuario contra MS-1 Auth via gRPC."""
        with grpc.insecure_channel(self._channel_target()) as channel:
            stub = auth_pb2_grpc.AuthServiceStub(channel)
            request = auth_pb2.CheckRoleRequest(user_id=str(user_id), role=role)
            try:
                response = stub.CheckRole(request, timeout=self.timeout)
            except grpc.RpcError as e:
                logger.error(
                    f"[AuthClient MS-7] Error gRPC al verificar rol: "
                    f"code={e.code()} detail={e.details()}"
                )
                raise

            return bool(response.allowed)

    def get_user_by_id(self, user_id: str) -> dict | None:
        """Obtiene el perfil de un usuario contra MS-1 Auth via gRPC."""
        with grpc.insecure_channel(self._channel_target()) as channel:
            stub = auth_pb2_grpc.AuthServiceStub(channel)
            request = auth_pb2.GetUserByIdRequest(user_id=str(user_id))
            try:
                response = stub.GetUserById(request, timeout=self.timeout)
            except grpc.RpcError as e:
                logger.error(
                    f"[AuthClient MS-7] Error gRPC al obtener usuario: "
                    f"code={e.code()} detail={e.details()}"
                )
                raise

            if not response.found:
                return None

            user = response.user
            return {
                "user_id": user.user_id,
                "nombre_completo": user.nombre_completo,
                "email": user.email,
                "role": user.role,
                "activo": user.activo,
            }


# Instancia compartida (canal se abre por llamada, sin estado persistente)
auth_client = AuthClient()
