"""
Dependencias de autenticación y autorización para MS-Notificaciones (MS-6).
Valida tokens JWT contra MS-Auth (MS-1) vía RabbitMQ con fallback gRPC.
"""
from fastapi import Header, HTTPException, Depends
from app.messaging.clients.auth_hybrid_client import auth_client


async def get_current_user(authorization: str = Header(...)) -> dict:
    """Extrae y valida el Bearer token usando el cliente híbrido de MS-Auth."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Token inválido. Formato esperado: 'Bearer <token>'"
        )

    token = authorization.split(" ", 1)[1]
    result = await auth_client.validate_token(token)

    if not result or not result.get("valid"):
        msg = result.get("error", "Sesión no válida") if result else "No se pudo conectar con MS-Auth"
        raise HTTPException(status_code=401, detail=msg)

    return result


def role_required(role_name: str):
    """
    Dependencia factory: solo permite el acceso si el usuario tiene el rol indicado.
    Normaliza alias comunes: ADMINISTRADOR → ADMIN.
    """
    async def checker(user: dict = Depends(get_current_user)) -> dict:
        actual_role   = user.get("role", "").upper()
        required_role = role_name.upper()

        _ALIAS = {"ADMINISTRADOR": "ADMIN", "DOCENTE": "DOCENTE", "ALUMNO": "ALUMNO"}
        actual_role   = _ALIAS.get(actual_role, actual_role)
        required_role = _ALIAS.get(required_role, required_role)

        if actual_role != required_role:
            raise HTTPException(
                status_code=403,
                detail=f"Permisos insuficientes. Tu rol es '{actual_role}', se requiere '{required_role}'"
            )
        return user

    return checker

def roles_required(role_names: list[str]):
    """
    Dependencia factory: permite el acceso si el usuario tiene uno de los roles indicados.
    """
    async def checker(user: dict = Depends(get_current_user)) -> dict:
        actual_role   = user.get("role", "").upper()
        required_roles = [r.upper() for r in role_names]

        _ALIAS = {"ADMINISTRADOR": "ADMIN", "DOCENTE": "DOCENTE", "ALUMNO": "ALUMNO"}
        actual_role = _ALIAS.get(actual_role, actual_role)
        required_roles = [_ALIAS.get(r, r) for r in required_roles]

        if actual_role not in required_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Permisos insuficientes. Tu rol es '{actual_role}', se requiere uno de: {', '.join(required_roles)}"
            )
        return user

    return checker
