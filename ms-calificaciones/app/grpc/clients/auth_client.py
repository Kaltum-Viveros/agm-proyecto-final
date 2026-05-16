"""
Cliente gRPC hacia MS-Auth (MS-1).
Valida tokens JWT para proteger los endpoints de MS-Calificaciones.
"""
import grpc
import logging
from app.core.config import settings

try:
    from app.grpc.generated import auth_pb2, auth_pb2_grpc
    _PROTO_AVAILABLE = True
except ImportError:
    _PROTO_AVAILABLE = False
    logging.warning("[AuthClient MS-4] auth_pb2 no disponible.")


class AuthClient:
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
        Valida el Bearer token contra MS-Auth.
        Retorna dict con claims si es válido, None si no.
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
            logging.error(f"[AuthClient MS-4] Error gRPC al validar token: {e.details()}")
            return None


# Singleton
auth_client = AuthClient()
