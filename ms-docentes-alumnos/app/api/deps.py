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
        if user.role != role_name:
            raise HTTPException(status_code=403, detail="Permisos insuficientes")
        return user
    return checker