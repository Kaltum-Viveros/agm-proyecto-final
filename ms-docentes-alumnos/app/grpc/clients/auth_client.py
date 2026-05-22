import grpc
import logging
import os
from app.grpc.generated import auth_pb2, auth_pb2_grpc
from app.core.config import settings

logger = logging.getLogger(__name__)

class AuthClient:
    def __init__(self):
        # Leemos host y puerto desde las variables de entorno / settings
        self.host = os.getenv("MS1_HOST", "ms-auth")
        self.port = os.getenv("MS1_PORT", "50051")
        self.channel = grpc.insecure_channel(f"{self.host}:{self.port}")
        self.stub = auth_pb2_grpc.AuthServiceStub(self.channel)

    def validate_token(self, token: str):
        """Valida el JWT con el MS-1"""
        try:
            request = auth_pb2.ValidateTokenRequest(token=token)
            response = self.stub.ValidateToken(request)
            return response if response.valid else None
        except grpc.RpcError as e:
            logger.error(f"[AuthClient] Error gRPC ValidateToken: {e.details()}")
            return None

    def get_user_by_id(self, user_id: str):
        """Obtiene el perfil de usuario desde MS-1"""
        try:
            request = auth_pb2.GetUserByIdRequest(user_id=user_id)
            response = self.stub.GetUserById(request)
            return response.user if response.found else None
        except grpc.RpcError as e:
            logger.error(f"[AuthClient] Error gRPC GetUserById: {e.details()}")
            return None

    def check_role(self, user_id: str, role: str):
        """Verifica si un usuario tiene un rol específico en MS-1"""
        try:
            request = auth_pb2.CheckRoleRequest(user_id=user_id, role=role)
            response = self.stub.CheckRole(request)
            return response.allowed
        except grpc.RpcError as e:
            logger.error(f"[AuthClient] Error gRPC CheckRole: {e.details()}")
            return False

    def crear_identidad(self, nombre: str, email: str, role: str = "Alumno"):
        """
        Registra al usuario (Alumno o Docente) y obtiene su user_id real desde MS-1.

        Eleva grpc.RpcError si MS-1 no está disponible o hay error de conexión,
        permitiendo al llamador distinguir entre fallo de red (503) y fallo de
        negocio (400/409).

        Devuelve (user_id: str, temp_password: str | None) si la identidad fue
        creada o recuperada correctamente.
        Devuelve (None, None) si MS-1 respondió pero no pudo entregar user_id
        por razón de negocio (datos inválidos, conflicto, etc.).
        """
        request = auth_pb2.CreateOrGetUserIdentityRequest(
            nombre_completo=nombre,
            email=email,
            role=role
        )
        # Dejamos que grpc.RpcError se propague hacia arriba intencionalmente.
        response = self.stub.CreateOrGetUserIdentity(request)
        user_id = response.user.user_id if response.user else None
        if response.created or user_id:
            return user_id, response.temporary_password
        return None, None