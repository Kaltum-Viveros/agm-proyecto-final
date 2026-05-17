from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.grpc_clients.cliente_auth import cliente_auth

# Instancia para extraer el token Bearer del header Authorization
security = HTTPBearer()

async def obtener_claims_usuario(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Llama a MS-Auth por gRPC usando validar_token.
    Si el token es inválido, expirado o revocado, lanza error 401.
    Si es válido, devuelve los claims.
    """
    token = credentials.credentials
    claims = await cliente_auth.validar_token(token)
    
    if not claims:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not claims.get("activo", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario está inactivo",
        )
        
    return claims

def requerir_rol(roles_permitidos: list[str]):
    """
    Dependencia de fábrica que retorna una función para validar roles específicos.
    """
    async def validador(claims: dict = Depends(obtener_claims_usuario)) -> dict:
        rol_usuario = claims.get("role", "").upper()
        if rol_usuario not in [r.upper() for r in roles_permitidos]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permisos insuficientes. Se requiere uno de los siguientes roles: {', '.join(roles_permitidos)}"
            )
        return claims
    return validador

# Dependencias listas para inyectarse en los endpoints
requerir_docente = requerir_rol(["DOCENTE", "ADMIN"])
requerir_alumno = requerir_rol(["ALUMNO", "ADMIN"])
requerir_usuario = obtener_claims_usuario # Cualquier usuario autenticado
