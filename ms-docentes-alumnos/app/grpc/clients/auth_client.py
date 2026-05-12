import grpc
import os
from app.grpc.generated import auth_pb2, auth_pb2_grpc

class AuthClient:
    def __init__(self):
        self.host = os.getenv("MS1_HOST", "ms-auth")
        self.port = os.getenv("MS1_PORT", "50051")
        self.channel = grpc.insecure_channel(f"{self.host}:{self.port}")
        self.stub = auth_pb2_grpc.AuthServiceStub(self.channel)

    def validar_token(self, token: str):
        """Valida el JWT con el MS-1"""
        try:
            request = auth_pb2.ValidateTokenRequest(token=token)
            response = self.stub.ValidateToken(request)
            return response if response.valid else None
        except Exception as e:
            print(f"Error gRPC MS-1: {e}")
            return None

    def crear_identidad_alumno(self, nombre: str, email: str):
        """Registra al alumno y obtiene su user_id real"""
        try:
            request = auth_pb2.CreateOrGetUserIdentityRequest(
                nombre_completo=nombre,
                email=email,
                role="Alumno"
            )
            response = self.stub.CreateOrGetUserIdentity(request)
            # Retornamos user_id y password temporal según el contrato
            if response.user.user_id:
                return response.user.user_id, response.temporary_password
            return None, None
        except Exception as e:
            print(f"Error al crear identidad en MS-1: {e}")
            return None, None