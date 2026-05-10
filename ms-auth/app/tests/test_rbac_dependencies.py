import pytest

from app.api.dependencies import validate_user_role
from app.models.enums import UserRole
from app.services.rbac_service import ForbiddenRoleError


def test_validate_user_role_dependency_returns_user_when_allowed() -> None:
    current_user = {
        "user_id": "1",
        "email": "admin@correo.com",
        "rol": "ADMIN",
    }

    result = validate_user_role(
        current_user=current_user,
        allowed_roles=[UserRole.ADMIN],
    )

    assert result == current_user


def test_validate_user_role_dependency_accepts_multiple_roles() -> None:
    current_user = {
        "user_id": "1",
        "email": "docente@correo.com",
        "rol": "DOCENTE",
    }

    result = validate_user_role(
        current_user=current_user,
        allowed_roles=[
            UserRole.ADMIN,
            UserRole.DOCENTE,
        ],
    )

    assert result == current_user


def test_validate_user_role_dependency_raises_error_when_role_is_not_allowed() -> None:
    current_user = {
        "user_id": "1",
        "email": "alumno@correo.com",
        "rol": "ALUMNO",
    }

    with pytest.raises(ForbiddenRoleError):
        validate_user_role(
            current_user=current_user,
            allowed_roles=[UserRole.ADMIN],
        )