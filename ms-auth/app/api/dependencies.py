from typing import Any, Callable, Dict, Iterable, Optional

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.enums import UserRole
from app.services.auth_service import AuthService
from app.services.rbac_service import ForbiddenRoleError, RBACService


def get_bearer_token(
    authorization: Optional[str] = Header(default=None),
) -> str:
    if authorization is None:
        return ""

    parts = authorization.strip().split()

    if len(parts) != 2:
        return ""

    scheme = parts[0]
    token = parts[1]

    if scheme.lower() != "bearer":
        return ""

    return token


def get_current_authenticated_user(
    access_token: str = Depends(get_bearer_token),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    auth_service = AuthService(db=db)

    return auth_service.get_current_user(
        access_token=access_token,
    )


def validate_user_role(
    current_user: Dict[str, Any],
    allowed_roles: Iterable[UserRole],
) -> Dict[str, Any]:
    rbac_service = RBACService()

    return rbac_service.validate_user_role(
        current_user=current_user,
        allowed_roles=allowed_roles,
    )


def require_roles(
    *allowed_roles: UserRole,
) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    def dependency(
        current_user: Dict[str, Any] = Depends(get_current_authenticated_user),
    ) -> Dict[str, Any]:
        return validate_user_role(
            current_user=current_user,
            allowed_roles=allowed_roles,
        )

    return dependency


def require_admin(
    current_user: Dict[str, Any] = Depends(get_current_authenticated_user),
) -> Dict[str, Any]:
    return validate_user_role(
        current_user=current_user,
        allowed_roles=[UserRole.ADMIN],
    )


def require_docente(
    current_user: Dict[str, Any] = Depends(get_current_authenticated_user),
) -> Dict[str, Any]:
    return validate_user_role(
        current_user=current_user,
        allowed_roles=[UserRole.DOCENTE],
    )


def require_alumno(
    current_user: Dict[str, Any] = Depends(get_current_authenticated_user),
) -> Dict[str, Any]:
    return validate_user_role(
        current_user=current_user,
        allowed_roles=[UserRole.ALUMNO],
    )


__all__ = [
    "ForbiddenRoleError",
    "get_bearer_token",
    "get_current_authenticated_user",
    "require_admin",
    "require_alumno",
    "require_docente",
    "require_roles",
    "validate_user_role",
]