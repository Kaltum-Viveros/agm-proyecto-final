from fastapi import Header, HTTPException, Depends
from app.grpc.clients.auth_client import AuthClient

auth_client = AuthClient()

async def get_current_user(authorization: str = Header(...)):
    """Extrae y valida el token usando el cliente gRPC"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token inválido")
    
    token = authorization.split(" ")[1]
    res = auth_client.validate_token(token)
    
    if not res or not res.valid:
        raise HTTPException(status_code=401, detail="Sesión no válida")
    return res.claims

def role_required(role_name: str):
    """Filtra el acceso por rol"""
    async def checker(user = Depends(get_current_user)):
        # Normalizamos a mayúsculas para que coincida con los Enums de MS-Auth (ADMIN, DOCENTE, ALUMNO)
        actual_role = user.role.upper()
        required_role = role_name.upper()
        
        # Mapeo de "ADMINISTRADOR" a "ADMIN" si es necesario
        if required_role == "ADMINISTRADOR": required_role = "ADMIN"
        if actual_role == "ADMINISTRADOR": actual_role = "ADMIN"

        if actual_role != required_role:
            raise HTTPException(status_code=403, detail=f"Permisos insuficientes. Tu rol es {actual_role}, se requiere {required_role}")
        return user
    return checker