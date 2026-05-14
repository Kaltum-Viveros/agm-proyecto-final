import grpc
import os
from app.grpc.generated import auth_pb2, auth_pb2_grpc
from app.core.config import settings

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
            print(f"Error gRPC ValidateToken (MS-1): {e.details()}")
            return None

    def get_user_by_id(self, user_id: str):
        """Obtiene el perfil de usuario desde MS-1"""
        try:
            request = auth_pb2.GetUserByIdRequest(user_id=user_id)
            response = self.stub.GetUserById(request)
            return response.user if response.found else None
        except grpc.RpcError as e:
            print(f"Error gRPC GetUserById (MS-1): {e.details()}")
            return None

    def check_role(self, user_id: str, role: str):
        """Verifica si un usuario tiene un rol específico en MS-1"""
        try:
            request = auth_pb2.CheckRoleRequest(user_id=user_id, role=role)
            response = self.stub.CheckRole(request)
            return response.allowed
        except grpc.RpcError as e:
            print(f"Error gRPC CheckRole (MS-1): {e.details()}")
            return False

    def crear_identidad(self, nombre: str, email: str, role: str = "Alumno"):
        """Registra al usuario (Alumno o Docente) y obtiene su user_id real"""
        try:
            request = auth_pb2.CreateOrGetUserIdentityRequest(
                nombre_completo=nombre,
                email=email,
                role=role
            )
            response = self.stub.CreateOrGetUserIdentity(request)
            if response.created or response.user.user_id:
                return response.user.user_id, response.temporary_password
            return None, None
        except grpc.RpcError as e:
            print(f"Error al crear identidad en MS-1: {e.details()}")
            return None, None