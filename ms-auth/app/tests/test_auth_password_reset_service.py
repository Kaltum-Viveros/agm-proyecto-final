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
    InvalidPasswordResetTokenError,
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


def build_password_reset_token(
    user_id,
    token_hash: str,
    expired: bool = False,
) -> AuthToken:
    expiration = utc_now() + timedelta(minutes=15)

    if expired:
        expiration = utc_now() - timedelta(minutes=1)

    return AuthToken(
        auth_token_id=uuid4(),
        user_id=user_id,
        token_type=TokenType.PASSWORD_RESET,
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


def test_request_password_reset_creates_password_reset_token() -> None:
    user = build_user()

    user_repository = MagicMock()
    user_repository.get_by_email.return_value = user

    auth_token_repository = MagicMock()

    token_service = TokenService()

    service = build_auth_service(
        user_repository=user_repository,
        auth_token_repository=auth_token_repository,
        token_service=token_service,
    )

    result = service.request_password_reset(" ADMIN@CORREO.COM ")

    assert result["reset_requested"] is True
    assert result["reset_token"]

    user_repository.get_by_email.assert_called_once_with("admin@correo.com")
    auth_token_repository.create.assert_called_once()

    create_kwargs = auth_token_repository.create.call_args.kwargs

    assert create_kwargs["user_id"] == user.user_id
    assert create_kwargs["token_type"] == TokenType.PASSWORD_RESET
    assert create_kwargs["token_hash"]
    assert create_kwargs["token_hash"] != result["reset_token"]
    assert create_kwargs["jti"] is None
    assert isinstance(create_kwargs["expiracion"], datetime)

    assert token_service.verify_token_hash(
        result["reset_token"],
        create_kwargs["token_hash"],
    )


def test_request_password_reset_does_not_reveal_unknown_email() -> None:
    user_repository = MagicMock()
    user_repository.get_by_email.return_value = None

    auth_token_repository = MagicMock()

    service = build_auth_service(
        user_repository=user_repository,
        auth_token_repository=auth_token_repository,
    )

    result = service.request_password_reset("noexiste@correo.com")

    assert result["reset_requested"] is True
    assert result["reset_token"] is None

    user_repository.get_by_email.assert_called_once_with("noexiste@correo.com")
    auth_token_repository.create.assert_not_called()


def test_request_password_reset_does_not_create_token_for_inactive_user() -> None:
    user = build_user(activo=False)

    user_repository = MagicMock()
    user_repository.get_by_email.return_value = user

    auth_token_repository = MagicMock()

    service = build_auth_service(
        user_repository=user_repository,
        auth_token_repository=auth_token_repository,
    )

    result = service.request_password_reset("admin@correo.com")

    assert result["reset_requested"] is True
    assert result["reset_token"] is None

    auth_token_repository.create.assert_not_called()


def test_reset_password_updates_password_and_marks_token_as_used() -> None:
    user = build_user()
    token_service = TokenService()

    reset_token = "valid-reset-token"
    reset_token_hash = token_service.hash_token(reset_token)

    stored_token = build_password_reset_token(
        user_id=user.user_id,
        token_hash=reset_token_hash,
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

    result = service.reset_password(
        reset_token=reset_token,
        nueva_contrasena="NewPassword123",
    )

    assert result["password_updated"] is True

    user_repository.get_by_id.assert_called_once_with(user.user_id)
    user_repository.update_password.assert_called_once()
    auth_token_repository.mark_as_used.assert_called_once_with(stored_token)

    update_args = user_repository.update_password.call_args.args

    assert update_args[0] == user
    assert update_args[1] != "NewPassword123"

    password_service = PasswordService()

    assert password_service.verify_password(
        "NewPassword123",
        update_args[1],
    )


def test_reset_password_rejects_invalid_token() -> None:
    user_repository = MagicMock()

    auth_token_repository = MagicMock()
    auth_token_repository.get_active_by_hash.return_value = None

    service = build_auth_service(
        user_repository=user_repository,
        auth_token_repository=auth_token_repository,
    )

    with pytest.raises(InvalidPasswordResetTokenError):
        service.reset_password(
            reset_token="invalid-reset-token",
            nueva_contrasena="NewPassword123",
        )

    user_repository.get_by_id.assert_not_called()
    user_repository.update_password.assert_not_called()
    auth_token_repository.mark_as_used.assert_not_called()


def test_reset_password_expires_expired_token() -> None:
    user = build_user()
    token_service = TokenService()

    reset_token = "expired-reset-token"
    reset_token_hash = token_service.hash_token(reset_token)

    stored_token = build_password_reset_token(
        user_id=user.user_id,
        token_hash=reset_token_hash,
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

    with pytest.raises(InvalidPasswordResetTokenError):
        service.reset_password(
            reset_token=reset_token,
            nueva_contrasena="NewPassword123",
        )

    auth_token_repository.expire.assert_called_once_with(stored_token)
    user_repository.get_by_id.assert_not_called()
    user_repository.update_password.assert_not_called()
    auth_token_repository.mark_as_used.assert_not_called()


def test_reset_password_rejects_when_user_not_found() -> None:
    user = build_user()
    token_service = TokenService()

    reset_token = "valid-reset-token"
    reset_token_hash = token_service.hash_token(reset_token)

    stored_token = build_password_reset_token(
        user_id=user.user_id,
        token_hash=reset_token_hash,
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

    with pytest.raises(InvalidPasswordResetTokenError):
        service.reset_password(
            reset_token=reset_token,
            nueva_contrasena="NewPassword123",
        )

    auth_token_repository.revoke.assert_called_once_with(stored_token)
    user_repository.update_password.assert_not_called()
    auth_token_repository.mark_as_used.assert_not_called()


def test_reset_password_rejects_inactive_user() -> None:
    user = build_user(activo=False)
    token_service = TokenService()

    reset_token = "valid-reset-token"
    reset_token_hash = token_service.hash_token(reset_token)

    stored_token = build_password_reset_token(
        user_id=user.user_id,
        token_hash=reset_token_hash,
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
        service.reset_password(
            reset_token=reset_token,
            nueva_contrasena="NewPassword123",
        )

    user_repository.update_password.assert_not_called()
    auth_token_repository.mark_as_used.assert_not_called()