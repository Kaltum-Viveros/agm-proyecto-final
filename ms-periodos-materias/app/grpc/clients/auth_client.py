"""
Cliente gRPC hacia MS-Auth (MS-1).
Permite al MS-2 validar tokens JWT y verificar roles de usuario.
"""
import grpc
import logging
from app.core.config import settings

try:
    from app.grpc.generated import auth_pb2, auth_pb2_grpc
    _PROTO_AVAILABLE = True
except ImportError:
    _PROTO_AVAILABLE = False
    logging.warning("auth_pb2 no disponible. Ejecuta compile_all_protos.py")


class AuthClient:
    """Cliente gRPC sincrónico hacia MS-Auth."""

    def __init__(self):
        self._channel = None
        self._stub = None

    def _get_stub(self):
        if not _PROTO_AVAILABLE:
            return None
        if self._stub is None:
            host = settings.ms_auth_grpc_host
            port = settings.ms_auth_grpc_port
            self._channel = grpc.insecure_channel(f"{host}:{port}")
            self._stub = auth_pb2_grpc.AuthServiceStub(self._channel)
        return self._stub

    def validate_token(self, token: str) -> dict | None:
        """
        Valida un Bearer token contra MS-Auth.
        Retorna un dict con los claims si es válido, None si no.
        """
        stub = self._get_stub()
        if not stub:
            return None
        try:
            response = stub.ValidateToken(
                auth_pb2.ValidateTokenRequest(token=token)
            )
            if response.valid:
                return {
                    "valid": True,
                    "user_id": response.claims.user_id,
                    "email":   response.claims.email,
                    "role":    response.claims.role,
                    "activo":  response.claims.activo,
                }
            return {"valid": False, "error": response.message}
        except grpc.RpcError as e:
            logging.error(f"[AuthClient] Error gRPC al validar token: {e.details()}")
            return None

    def check_role(self, user_id: str, role: str) -> bool:
        """
        Verifica si el usuario tiene el rol indicado.
        Retorna True si tiene permiso, False en cualquier otro caso.
        """
        stub = self._get_stub()
        if not stub:
            return False
        try:
            response = stub.CheckRole(
                auth_pb2.CheckRoleRequest(user_id=user_id, role=role)
            )
            return response.allowed
        except grpc.RpcError as e:
            logging.error(f"[AuthClient] Error gRPC al verificar rol: {e.details()}")
            return False


# Instancia singleton
auth_client = AuthClient()
