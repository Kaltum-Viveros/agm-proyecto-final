from typing import Dict, Any
from uuid import UUID

from app.db.session import SessionLocal
from app.services.auth_service import (
    AuthService,
    AccessTokenExpiredError,
    InvalidAccessTokenError,
    InactiveUserError,
    InvalidUserIdentityDataError,
)

async def validate_token_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    token = payload.get("token", "")
    
    db = SessionLocal()
    try:
        auth_service = AuthService(db=db)
        claims = auth_service.validate_access_token_claims(access_token=token)
        return {
            "valid": True,
            "claims": {
                "user_id": claims["user_id"],
                "email": claims["email"],
                "role": claims["role"],
                "jti": claims["jti"],
                "activo": claims["activo"]
            },
            "error_code": "",
            "message": "Token valido"
        }
    except AccessTokenExpiredError:
        return {
            "valid": False,
            "claims": {},
            "error_code": "AUTH_ACCESS_TOKEN_EXPIRED",
            "message": "Access token expirado"
        }
    except InvalidAccessTokenError:
        return {
            "valid": False,
            "claims": {},
            "error_code": "AUTH_INVALID_ACCESS_TOKEN",
            "message": "Access token invalido"
        }
    except InactiveUserError:
        return {
            "valid": False,
            "claims": {},
            "error_code": "AUTH_INACTIVE_USER",
            "message": "Usuario inactivo"
        }
    finally:
        db.close()

async def get_user_by_id_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    user_id_raw = payload.get("user_id")
    try:
        user_id = UUID(str(user_id_raw))
    except (ValueError, TypeError):
        return {
            "found": False,
            "user": {},
            "error_code": "AUTH_INVALID_USER_ID",
            "message": "User ID invalido"
        }

    db = SessionLocal()
    try:
        auth_service = AuthService(db=db)
        user = auth_service.get_user_profile_by_id(user_id)
        if user is None:
            return {
                "found": False,
                "user": {},
                "error_code": "AUTH_USER_NOT_FOUND",
                "message": "Usuario no encontrado"
            }
        return {
            "found": True,
            "user": {
                "user_id": user["user_id"],
                "nombre_completo": user["nombre_completo"],
                "email": user["email"],
                "role": user["rol"],
                "activo": user["activo"]
            },
            "error_code": "",
            "message": "Usuario encontrado"
        }
    finally:
        db.close()

async def check_role_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    user_id_raw = payload.get("user_id")
    role = payload.get("role")
    
    try:
        user_id = UUID(str(user_id_raw))
    except (ValueError, TypeError):
        return {
            "allowed": False,
            "error_code": "AUTH_INVALID_USER_ID",
            "message": "User ID invalido"
        }

    db = SessionLocal()
    try:
        auth_service = AuthService(db=db)
        allowed = auth_service.check_user_role(user_id=user_id, role=role)
        if not allowed:
            return {
                "allowed": False,
                "error_code": "AUTH_ROLE_NOT_ALLOWED",
                "message": "Rol no autorizado"
            }
        return {
            "allowed": True,
            "error_code": "",
            "message": "Rol autorizado"
        }
    finally:
        db.close()

async def create_or_get_user_identity_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    nombre_completo = payload.get("nombre_completo", "")
    email = payload.get("email", "")
    role = payload.get("role", "")
    
    db = SessionLocal()
    try:
        auth_service = AuthService(db=db)
        result = auth_service.create_or_get_user_identity(
            nombre_completo=nombre_completo,
            email=email,
            role=role
        )
        return {
            "created": result["created"],
            "user": {
                "user_id": result["user"]["user_id"],
                "nombre_completo": result["user"]["nombre_completo"],
                "email": result["user"]["email"],
                "role": result["user"]["rol"],
                "activo": result["user"]["activo"]
            },
            "temporary_password": result["temporary_password"],
            "error_code": "",
            "message": "Identidad procesada correctamente"
        }
    except InvalidUserIdentityDataError as exc:
        return {
            "created": False,
            "user": {},
            "temporary_password": "",
            "error_code": "AUTH_INVALID_USER_IDENTITY_DATA",
            "message": str(exc)
        }
    finally:
        db.close()
