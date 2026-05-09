from datetime import timedelta
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.models.auth_token import AuthToken
from app.models.enums import TokenStatus, TokenType, UserRole
from app.models.user import User
from app.services.auth_service import (
    AccessTokenExpiredError,
    AuthService,
    InactiveUserError,
    InvalidAccessTokenError,
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
    jwt_service: JWTService,
) -> AuthService:
    return AuthService(
        user_repository=user_repository,
        auth_token_repository=auth_token_repository,
        password_service=PasswordService(),
        jwt_service=jwt_service,
        token_service=TokenService(),
    )


def test_get_current_user_returns_user_from_valid_access_token() -> None:
    user = build_user()

    jwt_service = JWTService(
        secret_key="test-secret",
        algorithm="HS256",
        access_token_expire_minutes=15,
    )

    access_token = jwt_service.create_access_token(
        user_id=user.user_id,
        email=user.email,
        rol=user.rol,
    )

    user_repository = MagicMock()
    user_repository.get_by_id.return_value = user

    auth_token_repository = MagicMock()
    auth_token_repository.get_active_revoked_access_by_jti.return_value = None

    service = build_auth_service(
        user_repository=user_repository,
        auth_token_repository=auth_token_repository,
        jwt_service=jwt_service,
    )

    result = service.get_current_user(access_token)

    assert result["user_id"] == str(user.user_id)
    assert result["email"] == user.email
    assert result["rol"] == UserRole.ADMIN.value
    assert result["activo"] is True

    user_repository.get_by_id.assert_called_once_with(user.user_id)
    auth_token_repository.get_active_revoked_access_by_jti.assert_called_once()


def test_get_current_user_rejects_empty_access_token() -> None:
    jwt_service = JWTService(
        secret_key="test-secret",
        algorithm="HS256",
        access_token_expire_minutes=15,
    )

    user_repository = MagicMock()
    auth_token_repository = MagicMock()

    service = build_auth_service(
        user_repository=user_repository,
        auth_token_repository=auth_token_repository,
        jwt_service=jwt_service,
    )

    with pytest.raises(InvalidAccessTokenError):
        service.get_current_user("")

    user_repository.get_by_id.assert_not_called()
    auth_token_repository.get_active_revoked_access_by_jti.assert_not_called()


def test_get_current_user_rejects_expired_access_token() -> None:
    user = build_user()

    jwt_service = JWTService(
        secret_key="test-secret",
        algorithm="HS256",
        access_token_expire_minutes=15,
    )

    access_token = jwt_service.create_access_token(
        user_id=user.user_id,
        email=user.email,
        rol=user.rol,
        expires_delta=timedelta(minutes=-1),
    )

    user_repository = MagicMock()
    auth_token_repository = MagicMock()

    service = build_auth_service(
        user_repository=user_repository,
        auth_token_repository=auth_token_repository,
        jwt_service=jwt_service,
    )

    with pytest.raises(AccessTokenExpiredError):
        service.get_current_user(access_token)

    user_repository.get_by_id.assert_not_called()
    auth_token_repository.get_active_revoked_access_by_jti.assert_not_called()


def test_get_current_user_rejects_revoked_access_token() -> None:
    user = build_user()

    jwt_service = JWTService(
        secret_key="test-secret",
        algorithm="HS256",
        access_token_expire_minutes=15,
    )

    access_token = jwt_service.create_access_token(
        user_id=user.user_id,
        email=user.email,
        rol=user.rol,
    )

    payload = jwt_service.decode_token(access_token)

    revoked_token = AuthToken(
        user_id=user.user_id,
        token_type=TokenType.REVOKED_ACCESS,
        jti=payload["jti"],
        expiracion=payload["exp"],
        estado=TokenStatus.ACTIVE,
    )

    user_repository = MagicMock()

    auth_token_repository = MagicMock()
    auth_token_repository.get_active_revoked_access_by_jti.return_value = revoked_token

    service = build_auth_service(
        user_repository=user_repository,
        auth_token_repository=auth_token_repository,
        jwt_service=jwt_service,
    )

    with pytest.raises(InvalidAccessTokenError):
        service.get_current_user(access_token)

    user_repository.get_by_id.assert_not_called()
    auth_token_repository.get_active_revoked_access_by_jti.assert_called_once_with(
        jti=payload["jti"],
    )


def test_get_current_user_rejects_when_user_not_found() -> None:
    user = build_user()

    jwt_service = JWTService(
        secret_key="test-secret",
        algorithm="HS256",
        access_token_expire_minutes=15,
    )

    access_token = jwt_service.create_access_token(
        user_id=user.user_id,
        email=user.email,
        rol=user.rol,
    )

    user_repository = MagicMock()
    user_repository.get_by_id.return_value = None

    auth_token_repository = MagicMock()
    auth_token_repository.get_active_revoked_access_by_jti.return_value = None

    service = build_auth_service(
        user_repository=user_repository,
        auth_token_repository=auth_token_repository,
        jwt_service=jwt_service,
    )

    with pytest.raises(InvalidAccessTokenError):
        service.get_current_user(access_token)

    user_repository.get_by_id.assert_called_once_with(user.user_id)


def test_get_current_user_rejects_inactive_user() -> None:
    user = build_user(activo=False)

    jwt_service = JWTService(
        secret_key="test-secret",
        algorithm="HS256",
        access_token_expire_minutes=15,
    )

    access_token = jwt_service.create_access_token(
        user_id=user.user_id,
        email=user.email,
        rol=user.rol,
    )

    user_repository = MagicMock()
    user_repository.get_by_id.return_value = user

    auth_token_repository = MagicMock()
    auth_token_repository.get_active_revoked_access_by_jti.return_value = None

    service = build_auth_service(
        user_repository=user_repository,
        auth_token_repository=auth_token_repository,
        jwt_service=jwt_service,
    )

    with pytest.raises(InactiveUserError):
        service.get_current_user(access_token)

    user_repository.get_by_id.assert_called_once_with(user.user_id)