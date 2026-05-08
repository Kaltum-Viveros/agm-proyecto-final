from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.models.enums import UserRole
from app.models.user import User
from app.services.password_service import PasswordService
from scripts.seed_admin import normalize_email, seed_admin_user


def build_existing_admin() -> User:
    return User(
        user_id=uuid4(),
        nombre_completo="Administrador AGM",
        email="admin@agm.com",
        contrasena_hash="hashed-password",
        rol=UserRole.ADMIN,
        activo=True,
    )


def test_normalize_email_trims_and_lowercases() -> None:
    assert normalize_email(" ADMIN@AGM.COM ") == "admin@agm.com"


def test_seed_admin_returns_existing_user_without_creating() -> None:
    existing_user = build_existing_admin()

    user_repository = MagicMock()
    user_repository.get_by_email.return_value = existing_user

    password_service = PasswordService()

    result = seed_admin_user(
        user_repository=user_repository,
        password_service=password_service,
        nombre_completo="Administrador AGM",
        email="admin@agm.com",
        password="Admin12345",
    )

    assert result["created"] is False
    assert result["user"] == existing_user

    user_repository.get_by_email.assert_called_once_with("admin@agm.com")
    user_repository.create.assert_not_called()


def test_seed_admin_creates_user_when_not_exists() -> None:
    user_repository = MagicMock()
    user_repository.get_by_email.return_value = None

    created_user = build_existing_admin()
    user_repository.create.return_value = created_user

    password_service = PasswordService()

    result = seed_admin_user(
        user_repository=user_repository,
        password_service=password_service,
        nombre_completo=" Administrador AGM ",
        email=" ADMIN@AGM.COM ",
        password="Admin12345",
    )

    assert result["created"] is True
    assert result["user"] == created_user

    user_repository.get_by_email.assert_called_once_with("admin@agm.com")
    user_repository.create.assert_called_once()

    create_kwargs = user_repository.create.call_args.kwargs

    assert create_kwargs["nombre_completo"] == "Administrador AGM"
    assert create_kwargs["email"] == "admin@agm.com"
    assert create_kwargs["rol"] == UserRole.ADMIN
    assert create_kwargs["activo"] is True
    assert create_kwargs["contrasena_hash"] != "Admin12345"

    assert password_service.verify_password(
        "Admin12345",
        create_kwargs["contrasena_hash"],
    )


def test_seed_admin_rejects_empty_password() -> None:
    user_repository = MagicMock()
    password_service = PasswordService()

    with pytest.raises(ValueError):
        seed_admin_user(
            user_repository=user_repository,
            password_service=password_service,
            nombre_completo="Administrador AGM",
            email="admin@agm.com",
            password="",
        )

    user_repository.get_by_email.assert_not_called()
    user_repository.create.assert_not_called()


def test_seed_admin_rejects_short_password() -> None:
    user_repository = MagicMock()
    password_service = PasswordService()

    with pytest.raises(ValueError):
        seed_admin_user(
            user_repository=user_repository,
            password_service=password_service,
            nombre_completo="Administrador AGM",
            email="admin@agm.com",
            password="123",
        )

    user_repository.get_by_email.assert_not_called()
    user_repository.create.assert_not_called()