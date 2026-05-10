import pytest

from app.models.enums import UserRole
from app.services.rbac_service import ForbiddenRoleError, RBACService


def test_normalize_role_from_enum() -> None:
    service = RBACService()

    assert service.normalize_role(UserRole.ADMIN) == "ADMIN"


def test_normalize_role_from_string() -> None:
    service = RBACService()

    assert service.normalize_role(" docente ") == "DOCENTE"


def test_user_has_role_returns_true_for_allowed_role() -> None:
    service = RBACService()

    result = service.user_has_role(
        user_role=UserRole.ADMIN,
        allowed_roles=[UserRole.ADMIN],
    )

    assert result is True


def test_user_has_role_returns_true_when_role_string_matches() -> None:
    service = RBACService()

    result = service.user_has_role(
        user_role="docente",
        allowed_roles=[UserRole.DOCENTE],
    )

    assert result is True


def test_user_has_role_returns_false_for_disallowed_role() -> None:
    service = RBACService()

    result = service.user_has_role(
        user_role=UserRole.ALUMNO,
        allowed_roles=[UserRole.ADMIN, UserRole.DOCENTE],
    )

    assert result is False


def test_validate_user_role_returns_user_when_allowed() -> None:
    service = RBACService()

    current_user = {
        "user_id": "1",
        "email": "admin@correo.com",
        "rol": "ADMIN",
    }

    result = service.validate_user_role(
        current_user=current_user,
        allowed_roles=[UserRole.ADMIN],
    )

    assert result == current_user


def test_validate_user_role_raises_error_when_role_is_not_allowed() -> None:
    service = RBACService()

    current_user = {
        "user_id": "1",
        "email": "alumno@correo.com",
        "rol": "ALUMNO",
    }

    with pytest.raises(ForbiddenRoleError):
        service.validate_user_role(
            current_user=current_user,
            allowed_roles=[UserRole.ADMIN],
        )


def test_validate_user_role_raises_error_when_no_allowed_roles() -> None:
    service = RBACService()

    current_user = {
        "user_id": "1",
        "email": "admin@correo.com",
        "rol": "ADMIN",
    }

    with pytest.raises(ForbiddenRoleError):
        service.validate_user_role(
            current_user=current_user,
            allowed_roles=[],
        )