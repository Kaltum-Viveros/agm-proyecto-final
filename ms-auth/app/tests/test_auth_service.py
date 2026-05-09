from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.models.auth_token import AuthToken
from app.models.enums import TokenStatus, TokenType, UserRole
from app.models.user import User
from app.services.auth_service import (
    AuthService,
    InactiveUserError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
)
from app.services.jwt_service import JWTService
from app.services.password_service import PasswordService
from app.services.token_service import TokenService


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


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


def build_refresh_token(
    user_id,
    token_hash: str,
    expired: bool = False,
) -> AuthToken:
    expiration = utc_now() - timedelta(minutes=1)

    if not expired:
        expiration = utc_now() + timedelta(days=7)

    return AuthToken(
        auth_token_id=uuid4(),
        user_id=user_id,
        token_type=TokenType.REFRESH,
        token_hash=token_hash,
        expiracion=expiration,
        estado=TokenStatus.ACTIVE,
    )


def build_auth_service(
    user_repository: MagicMock,
    auth_token_repository: MagicMock,
    token_service: TokenService = None,
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
        token_service=token_service or TokenService(),
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


def test_refresh_session_returns_new_tokens_and_rotates_refresh_token() -> None:
    user = build_user()
    token_service = TokenService()

    old_refresh_token = "old-refresh-token"
    old_refresh_token_hash = token_service.hash_token(old_refresh_token)
    stored_token = build_refresh_token(
        user_id=user.user_id,
        token_hash=old_refresh_token_hash,
    )

    user_repository = MagicMock()
    user_repository.get_by_id.return_value = user

    auth_token_repository = MagicMock()
    auth_token_repository.get_active_by_hash.return_value = stored_token

    service = build_auth_service(
        user_repository=user_repository,
        auth_token_repository=auth_token_repository,
        token_service=token_service,
    )

    result = service.refresh_session(old_refresh_token)

    assert result["access_token"]
    assert result["refresh_token"]
    assert result["refresh_token"] != old_refresh_token
    assert result["token_type"] == "Bearer"
    assert result["expires_in"] == 900
    assert result["user"]["user_id"] == str(user.user_id)
    assert result["user"]["rol"] == UserRole.ADMIN.value

    auth_token_repository.get_active_by_hash.assert_called_once_with(
        token_hash=old_refresh_token_hash,
        token_type=TokenType.REFRESH,
    )
    user_repository.get_by_id.assert_called_once_with(user.user_id)
    auth_token_repository.mark_as_used.assert_called_once_with(stored_token)
    auth_token_repository.create.assert_called_once()

    create_kwargs = auth_token_repository.create.call_args.kwargs

    assert create_kwargs["user_id"] == user.user_id
    assert create_kwargs["token_type"] == TokenType.REFRESH
    assert create_kwargs["token_hash"]
    assert create_kwargs["token_hash"] != old_refresh_token_hash
    assert create_kwargs["expiracion"] == result["refresh_expires_at"]
    assert token_service.verify_token_hash(
        result["refresh_token"],
        create_kwargs["token_hash"],
    )


def test_refresh_session_raises_error_when_token_not_found() -> None:
    user_repository = MagicMock()

    auth_token_repository = MagicMock()
    auth_token_repository.get_active_by_hash.return_value = None

    service = build_auth_service(
        user_repository=user_repository,
        auth_token_repository=auth_token_repository,
    )

    with pytest.raises(InvalidRefreshTokenError):
        service.refresh_session("invalid-refresh-token")

    user_repository.get_by_id.assert_not_called()
    auth_token_repository.mark_as_used.assert_not_called()
    auth_token_repository.create.assert_not_called()


def test_refresh_session_expires_token_when_token_is_expired() -> None:
    user = build_user()
    token_service = TokenService()

    refresh_token = "expired-refresh-token"
    refresh_token_hash = token_service.hash_token(refresh_token)
    stored_token = build_refresh_token(
        user_id=user.user_id,
        token_hash=refresh_token_hash,
        expired=True,
    )

    user_repository = MagicMock()

    auth_token_repository = MagicMock()
    auth_token_repository.get_active_by_hash.return_value = stored_token

    service = build_auth_service(
        user_repository=user_repository,
        auth_token_repository=auth_token_repository,
        token_service=token_service,
    )

    with pytest.raises(InvalidRefreshTokenError):
        service.refresh_session(refresh_token)

    auth_token_repository.expire.assert_called_once_with(stored_token)
    user_repository.get_by_id.assert_not_called()
    auth_token_repository.mark_as_used.assert_not_called()
    auth_token_repository.create.assert_not_called()


def test_refresh_session_raises_error_when_user_not_found() -> None:
    user = build_user()
    token_service = TokenService()

    refresh_token = "valid-refresh-token"
    refresh_token_hash = token_service.hash_token(refresh_token)
    stored_token = build_refresh_token(
        user_id=user.user_id,
        token_hash=refresh_token_hash,
    )

    user_repository = MagicMock()
    user_repository.get_by_id.return_value = None

    auth_token_repository = MagicMock()
    auth_token_repository.get_active_by_hash.return_value = stored_token

    service = build_auth_service(
        user_repository=user_repository,
        auth_token_repository=auth_token_repository,
        token_service=token_service,
    )

    with pytest.raises(InvalidRefreshTokenError):
        service.refresh_session(refresh_token)

    auth_token_repository.revoke.assert_called_once_with(stored_token)
    auth_token_repository.mark_as_used.assert_not_called()
    auth_token_repository.create.assert_not_called()


def test_refresh_session_raises_error_when_user_is_inactive() -> None:
    user = build_user(activo=False)
    token_service = TokenService()

    refresh_token = "valid-refresh-token"
    refresh_token_hash = token_service.hash_token(refresh_token)
    stored_token = build_refresh_token(
        user_id=user.user_id,
        token_hash=refresh_token_hash,
    )

    user_repository = MagicMock()
    user_repository.get_by_id.return_value = user

    auth_token_repository = MagicMock()
    auth_token_repository.get_active_by_hash.return_value = stored_token

    service = build_auth_service(
        user_repository=user_repository,
        auth_token_repository=auth_token_repository,
        token_service=token_service,
    )

    with pytest.raises(InactiveUserError):
        service.refresh_session(refresh_token)

    auth_token_repository.mark_as_used.assert_not_called()
    auth_token_repository.create.assert_not_called()