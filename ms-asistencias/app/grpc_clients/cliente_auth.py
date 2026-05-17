import logging

import grpc

from app.core.config import settings
from app.generated import auth_pb2, auth_pb2_grpc

class ClienteAuth:
    def __init__(self):
        self.target = f"{settings.AUTH_GRPC_HOST}:{settings.AUTH_GRPC_PORT}"
        self.channel = grpc.aio.insecure_channel(self.target)
        self.stub = auth_pb2_grpc.AuthServiceStub(self.channel)

    async def validar_token(self, token: str) -> dict:
        """
        Valida el JWT del usuario contra MS-1 (Auth).
        Retorna claims si es válido, o None si no lo es.
        """
        try:
            request = auth_pb2.ValidateTokenRequest(token=token)
            response = await self.stub.ValidateToken(request)
            if response.valid:
                return {
                    "user_id": response.claims.user_id,
                    "email": response.claims.email,
                    "role": response.claims.role,
                    "jti": response.claims.jti,
                    "activo": response.claims.activo,
                }
            return None
        except grpc.RpcError as e:
            logging.error(f"Error gRPC al conectar con MS-1 (Auth): {e.details()}")
            return None

    async def verificar_rol(self, user_id: str, role: str) -> bool:
        """
        Verifica si el usuario tiene el rol requerido usando MS-1 (Auth).
        """
        try:
            request = auth_pb2.CheckRoleRequest(user_id=user_id, role=role)
            response = await self.stub.CheckRole(request)
            return response.allowed
        except grpc.RpcError as e:
            logging.error(f"Error gRPC al conectar con MS-1 (Auth): {e.details()}")
            return False

cliente_auth = ClienteAuth()
