"""
Dependencias de autenticación para los endpoints REST de MS-7.
Valida tokens JWT contra MS-Auth (MS-1) vía gRPC.
"""
import grpc
from fastapi import Header, HTTPException, status

from app.grpc.clients.auth_client import auth_client

async def require_authenticated_user(authorization: str = Header(..., description="Bearer JWT token")) -> dict:
    """
    Dependencia FastAPI que extrae y valida el token JWT contra MS-1.
    Retorna los claims del usuario si es válido.
    Lanza HTTP 401 si no hay token, el formato es incorrecto, o es rechazado por MS-1.
    Lanza HTTP 503 si MS-1 no está disponible.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de token inválido. Se espera 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split(" ")[1]

    try:
        claims = auth_client.validate_token(token)
        return claims
    except ValueError as e:
        # El token es inválido o expirado (rechazado por MS-1)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except grpc.RpcError as e:
        # Error de conexión o disponibilidad de MS-1
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Servicio de autenticación no disponible: {e.details()}"
        )
