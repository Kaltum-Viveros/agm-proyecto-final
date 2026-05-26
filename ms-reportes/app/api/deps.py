"""
Dependencias de autenticacion para los endpoints REST de MS-7.
Valida tokens JWT contra MS-Auth (MS-1) via RabbitMQ con fallback gRPC.
"""
import aio_pika.exceptions
import aiormq.exceptions
import grpc
from fastapi import Header, HTTPException, status

from app.messaging.clients.auth_hybrid_client import auth_client
from shared.agm_messaging.exceptions import RPCException, RPCTimeoutException

_TRANSPORT_EXCEPTIONS = (
    TimeoutError,
    ConnectionError,
    OSError,
    RuntimeError,
    RPCException,
    RPCTimeoutException,
    aio_pika.exceptions.AMQPException,
    aiormq.exceptions.AMQPError,
)


async def require_authenticated_user(authorization: str = Header(..., description="Bearer JWT token")) -> dict:
    """
    Dependencia FastAPI que extrae y valida el token JWT contra MS-1.
    Retorna los claims del usuario si es valido.
    Lanza HTTP 401 si no hay token, el formato es incorrecto, o es rechazado por MS-1.
    Lanza HTTP 503 si MS-1 no esta disponible.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de token invalido. Se espera 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split(" ")[1]

    try:
        claims = await auth_client.validate_token(token)
        if not claims or not claims.get("valid"):
            detail = claims.get("error") if claims else "Token invalido o expirado"
            raise ValueError(detail)
        return claims
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except grpc.RpcError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Servicio de autenticacion no disponible: {e.details()}"
        )
    except _TRANSPORT_EXCEPTIONS as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Servicio de autenticacion no disponible: {e}"
        )
