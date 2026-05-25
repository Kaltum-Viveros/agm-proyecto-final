from fastapi import Header, HTTPException, Depends
from app.messaging.clients.auth_hybrid_client import auth_client

async def get_current_user(authorization: str = Header(...)):
    """Extrae y valida el token usando Auth por RabbitMQ con fallback gRPC."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token inválido")
    
    token = authorization.split(" ")[1]
    res = await auth_client.validate_token(token)
    
    if not res or not res.valid:
        raise HTTPException(status_code=401, detail="Sesión no válida")
    return res.claims

def role_required(*role_names: str):
    """Filtra el acceso por roles permitidos"""
    async def checker(user = Depends(get_current_user)):
        # Normalizamos a mayúsculas para que coincida con los Enums de MS-Auth (ADMIN, DOCENTE, ALUMNO)
        actual_role = user.role.upper()
        if actual_role == "ADMINISTRADOR": actual_role = "ADMIN"
        
        allowed_roles = []
        for name in role_names:
            normalized = name.upper()
            if normalized == "ADMINISTRADOR": normalized = "ADMIN"
            allowed_roles.append(normalized)

        if actual_role not in allowed_roles:
            roles_str = ", ".join(allowed_roles)
            raise HTTPException(status_code=403, detail=f"Permisos insuficientes. Tu rol es {actual_role}, se requiere uno de: {roles_str}")
        return user
    return checker
