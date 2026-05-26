from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.messaging.clients.auth_hybrid_client import cliente_auth

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
        
    # --- Resolver IDs específicos de MS-3 (Docentes y Alumnos) ---
    email = claims.get("email")
    role = claims.get("role", "").upper()
    
    if email:
        import logging
        from app.messaging.clients.docentes_hybrid_client import cliente_alumnos
        if role in ("DOCENTE", "ADMIN"):
            try:
                docente_info = await cliente_alumnos.obtener_docente_por_email(email)
                if docente_info:
                    claims["id_docente"] = docente_info["docente_id"]
                    claims["nombre_completo"] = docente_info["nombre_completo"]
            except Exception as e:
                logging.error(f"Error fetching docente profile from MS-3: {e}")
        if role in ("ALUMNO", "ADMIN"):
            try:
                alumno_info = await cliente_alumnos.obtener_alumno_por_email(email)
                if alumno_info:
                    claims["id_alumno"] = alumno_info["alumno_id"]
                    claims["nombre_completo"] = alumno_info["nombre_completo"]
                    claims["matricula"] = alumno_info["matricula"]
            except Exception as e:
                logging.error(f"Error fetching alumno profile from MS-3: {e}")
        
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
