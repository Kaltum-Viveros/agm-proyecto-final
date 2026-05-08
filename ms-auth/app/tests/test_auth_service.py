from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.models.enums import TokenType, UserRole
from app.models.user import User
from app.services.auth_service import (
    AuthService,
    InactiveUserError,
    InvalidCredentialsError,
)
from app.services.jwt_service import JWTService
from app.services.password_service import PasswordService
from app.services.token_service import TokenService


def build_user(
    email: str = "admin@correo.com",
    activo: bool = True,
) -> User:
    password_service = PasswordService()

    return User(
        user_id=uuid4(),
        nombre_completo="Usuario Test",
        email=email,
        contrasena_hash=password_service.hash_password("Password123"),
        rol=UserRole.ADMIN,
        activo=activo,
    )


def build_auth_service(
    user_repository: MagicMock,
    auth_token_repository: MagicMock,
) -> AuthService:
    return AuthService(
        user_repository=user_repository,
        auth_token_repository=auth_token_repository,
        password_service=PasswordService(),
        jwt_service=JWTService(
            secret_key="test-secret",
            algorithm="HS256",
            access_token_expire_minutes=15,
        ),
        token_service=TokenService(),
    )


def test_login_returns_access_and_refresh_tokens() -> None:
    user = build_user()

    user_repository = MagicMock()
    user_repository.get_by_email.return_value = user

    auth_token_repository = MagicMock()

    service = build_auth_service(
        user_repository=user_repository,
        auth_token_repository=auth_token_repository,
    )

    result = service.login(
        email=" ADMIN@CORREO.COM ",
        contrasena="Password123",
    )

    assert result["access_token"]
    assert result["refresh_token"]
    assert result["token_type"] == "Bearer"
    assert result["expires_in"] == 900
    assert result["user"]["user_id"] == str(user.user_id)
    assert result["user"]["email"] == "admin@correo.com"
    assert result["user"]["rol"] == UserRole.ADMIN.value
    assert result["user"]["activo"] is True

    user_repository.get_by_email.assert_called_once_with("admin@correo.com")
    auth_token_repository.create.assert_called_once()

    create_kwargs = auth_token_repository.create.call_args.kwargs

    assert create_kwargs["user_id"] == user.user_id
    assert create_kwargs["token_type"] == TokenType.REFRESH
    assert create_kwargs["token_hash"]
    assert create_kwargs["expiracion"] == result["refresh_expires_at"]


def test_login_stores_only_refresh_token_hash() -> None:
    user = build_user()

    user_repository = MagicMock()
    user_repository.get_by_email.return_value = user

    auth_token_repository = MagicMock()

    token_service = TokenService()

    service = AuthService(
        user_repository=user_repository,
        auth_token_repository=auth_token_repository,
        password_service=PasswordService(),
        jwt_service=JWTService(
            secret_key="test-secret",
            algorithm="HS256",
            access_token_expire_minutes=15,
        ),
        token_service=token_service,
    )

    result = service.login(
        email="admin@correo.com",
        contrasena="Password123",
    )

    create_kwargs = auth_token_repository.create.call_args.kwargs

    refresh_token = result["refresh_token"]
    refresh_token_hash = create_kwargs["token_hash"]

    assert refresh_token != refresh_token_hash
    assert token_service.verify_token_hash(refresh_token, refresh_token_hash)


def test_login_raises_error_when_user_not_found() -> None:
    user_repository = MagicMock()
    user_repository.get_by_email.return_value = None

    auth_token_repository = MagicMock()

    service = build_auth_service(
        user_repository=user_repository,
        auth_token_repository=auth_token_repository,
    )

    with pytest.raises(InvalidCredentialsError):
        service.login(
            email="noexiste@correo.com",
            contrasena="Password123",
        )

    auth_token_repository.create.assert_not_called()


def test_login_raises_error_when_password_is_invalid() -> None:
    user = build_user()

    user_repository = MagicMock()
    user_repository.get_by_email.return_value = user

    auth_token_repository = MagicMock()

    service = build_auth_service(
        user_repository=user_repository,
        auth_token_repository=auth_token_repository,
    )

    with pytest.raises(InvalidCredentialsError):
        service.login(
            email="admin@correo.com",
            contrasena="WrongPassword",
        )

    auth_token_repository.create.assert_not_called()


def test_login_raises_error_when_user_is_inactive() -> None:
    user = build_user(activo=False)

    user_repository = MagicMock()
    user_repository.get_by_email.return_value = user

    auth_token_repository = MagicMock()

    service = build_auth_service(
        user_repository=user_repository,
        auth_token_repository=auth_token_repository,
    )

    with pytest.raises(InactiveUserError):
        service.login(
            email="admin@correo.com",
            contrasena="Password123",
        )

    auth_token_repository.create.assert_not_called()