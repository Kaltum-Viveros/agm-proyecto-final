import logging

import grpc

from app.core.config import settings
from app.generated import auth_pb2, auth_pb2_grpc

class ClienteAuth:
    def __init__(self):
        self.target = f"{settings.AUTH_GRPC_HOST}:{settings.AUTH_GRPC_PORT}"
        self._channel = None
        self._stub = None
        self._loop = None

    @property
    def stub(self):
        import asyncio
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None

        if self._channel is None or self._loop != current_loop:
            self._loop = current_loop
            self._channel = grpc.aio.insecure_channel(self.target)
            self._stub = auth_pb2_grpc.AuthServiceStub(self._channel)
        return self._stub

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

    async def get_user_by_id(self, user_id: str) -> dict | None:
        """
        Obtiene el perfil del usuario desde MS-1 (Auth).
        """
        try:
            request = auth_pb2.GetUserByIdRequest(user_id=str(user_id))
            response = await self.stub.GetUserById(request)
            if not response.found:
                return None
            return {
                "user_id": response.user.user_id,
                "nombre_completo": response.user.nombre_completo,
                "email": response.user.email,
                "role": response.user.role,
                "activo": response.user.activo,
            }
        except grpc.RpcError as e:
            logging.error(f"Error gRPC al conectar con MS-1 (Auth): {e.details()}")
            return None

cliente_auth = ClienteAuth()
