from datetime import datetime, timedelta, timezone
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


def build_auth_service(
    user_repository: MagicMock,
    auth_token_repository: MagicMock,
    jwt_service: JWTService,
    token_service: TokenService = None,
) -> AuthService:
    return AuthService(
        user_repository=user_repository,
        auth_token_repository=auth_token_repository,
        password_service=PasswordService(),
        jwt_service=jwt_service,
        token_service=token_service or TokenService(),
    )


def build_refresh_token(
    user_id,
    token_hash: str,
    expired: bool = False,
) -> AuthToken:
    expiration = utc_now() + timedelta(days=7)

    if expired:
        expiration = utc_now() - timedelta(minutes=1)

    return AuthToken(
        auth_token_id=uuid4(),
        user_id=user_id,
        token_type=TokenType.REFRESH,
        token_hash=token_hash,
        expiracion=expiration,
        estado=TokenStatus.ACTIVE,
    )


def test_logout_revokes_access_token_and_refresh_token() -> None:
    user = build_user()

    jwt_service = JWTService(
        secret_key="test-secret",
        algorithm="HS256",
        access_token_expire_minutes=15,
    )
    token_service = TokenService()

    access_token = jwt_service.create_access_token(
        user_id=user.user_id,
        email=user.email,
        rol=user.rol,
    )
    payload = jwt_service.decode_token(access_token)

    refresh_token = "valid-refresh-token"
    refresh_token_hash = token_service.hash_token(refresh_token)
    stored_refresh_token = build_refresh_token(
        user_id=user.user_id,
        token_hash=refresh_token_hash,
    )

    user_repository = MagicMock()
    user_repository.get_by_id.return_value = user

    auth_token_repository = MagicMock()
    auth_token_repository.get_active_revoked_access_by_jti.return_value = None
    auth_token_repository.get_active_by_hash.return_value = stored_refresh_token

    service = build_auth_service(
        user_repository=user_repository,
        auth_token_repository=auth_token_repository,
        jwt_service=jwt_service,
        token_service=token_service,
    )

    result = service.logout(
        access_token=access_token,
        refresh_token=refresh_token,
    )

    assert result["logged_out"] is True
    assert result["access_token_revoked"] is True
    assert result["refresh_token_revoked"] is True

    user_repository.get_by_id.assert_called_once_with(user.user_id)
    auth_token_repository.get_active_revoked_access_by_jti.assert_called_once_with(
        jti=payload["jti"],
    )
    auth_token_repository.get_active_by_hash.assert_called_once_with(
        token_hash=refresh_token_hash,
        token_type=TokenType.REFRESH,
    )
    auth_token_repository.create.assert_called_once()
    auth_token_repository.revoke.assert_called_once_with(stored_refresh_token)

    create_kwargs = auth_token_repository.create.call_args.kwargs

    assert create_kwargs["user_id"] == user.user_id
    assert create_kwargs["token_type"] == TokenType.REVOKED_ACCESS
    assert create_kwargs["jti"] == payload["jti"]
    assert create_kwargs["token_hash"] is None
    assert isinstance(create_kwargs["expiracion"], datetime)


def test_logout_revokes_only_access_token_when_refresh_token_is_not_sent() -> None:
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

    result = service.logout(
        access_token=access_token,
    )

    assert result["logged_out"] is True
    assert result["access_token_revoked"] is True
    assert result["refresh_token_revoked"] is False

    auth_token_repository.get_active_by_hash.assert_not_called()
    auth_token_repository.revoke.assert_not_called()
    auth_token_repository.create.assert_called_once()


def test_logout_rejects_empty_access_token() -> None:
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
        service.logout(
            access_token="",
        )

    user_repository.get_by_id.assert_not_called()
    auth_token_repository.create.assert_not_called()


def test_logout_rejects_expired_access_token() -> None:
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
        service.logout(
            access_token=access_token,
        )

    user_repository.get_by_id.assert_not_called()
    auth_token_repository.create.assert_not_called()


def test_logout_rejects_already_revoked_access_token() -> None:
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

    revoked_access_token = AuthToken(
        user_id=user.user_id,
        token_type=TokenType.REVOKED_ACCESS,
        jti=payload["jti"],
        expiracion=utc_now() + timedelta(minutes=15),
        estado=TokenStatus.ACTIVE,
    )

    user_repository = MagicMock()

    auth_token_repository = MagicMock()
    auth_token_repository.get_active_revoked_access_by_jti.return_value = (
        revoked_access_token
    )

    service = build_auth_service(
        user_repository=user_repository,
        auth_token_repository=auth_token_repository,
        jwt_service=jwt_service,
    )

    with pytest.raises(InvalidAccessTokenError):
        service.logout(
            access_token=access_token,
        )

    user_repository.get_by_id.assert_not_called()
    auth_token_repository.create.assert_not_called()
    auth_token_repository.revoke.assert_not_called()


def test_logout_rejects_when_user_not_found() -> None:
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
        service.logout(
            access_token=access_token,
        )

    auth_token_repository.create.assert_not_called()
    auth_token_repository.revoke.assert_not_called()


def test_logout_rejects_inactive_user() -> None:
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
        service.logout(
            access_token=access_token,
        )

    auth_token_repository.create.assert_not_called()
    auth_token_repository.revoke.assert_not_called()


def test_logout_rejects_invalid_refresh_token() -> None:
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
    auth_token_repository.get_active_by_hash.return_value = None

    service = build_auth_service(
        user_repository=user_repository,
        auth_token_repository=auth_token_repository,
        jwt_service=jwt_service,
    )

    with pytest.raises(InvalidRefreshTokenError):
        service.logout(
            access_token=access_token,
            refresh_token="invalid-refresh-token",
        )

    auth_token_repository.create.assert_not_called()
    auth_token_repository.revoke.assert_not_called()


def test_logout_expires_expired_refresh_token() -> None:
    user = build_user()

    jwt_service = JWTService(
        secret_key="test-secret",
        algorithm="HS256",
        access_token_expire_minutes=15,
    )
    token_service = TokenService()

    access_token = jwt_service.create_access_token(
        user_id=user.user_id,
        email=user.email,
        rol=user.rol,
    )

    refresh_token = "expired-refresh-token"
    refresh_token_hash = token_service.hash_token(refresh_token)
    stored_refresh_token = build_refresh_token(
        user_id=user.user_id,
        token_hash=refresh_token_hash,
        expired=True,
    )

    user_repository = MagicMock()
    user_repository.get_by_id.return_value = user

    auth_token_repository = MagicMock()
    auth_token_repository.get_active_revoked_access_by_jti.return_value = None
    auth_token_repository.get_active_by_hash.return_value = stored_refresh_token

    service = build_auth_service(
        user_repository=user_repository,
        auth_token_repository=auth_token_repository,
        jwt_service=jwt_service,
        token_service=token_service,
    )

    with pytest.raises(InvalidRefreshTokenError):
        service.logout(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    auth_token_repository.expire.assert_called_once_with(stored_refresh_token)
    auth_token_repository.create.assert_not_called()
    auth_token_repository.revoke.assert_not_called()


def test_logout_rejects_refresh_token_from_another_user() -> None:
    user = build_user()
    another_user = build_user(email="otro@correo.com")

    jwt_service = JWTService(
        secret_key="test-secret",
        algorithm="HS256",
        access_token_expire_minutes=15,
    )
    token_service = TokenService()

    access_token = jwt_service.create_access_token(
        user_id=user.user_id,
        email=user.email,
        rol=user.rol,
    )

    refresh_token = "valid-refresh-token"
    refresh_token_hash = token_service.hash_token(refresh_token)
    stored_refresh_token = build_refresh_token(
        user_id=another_user.user_id,
        token_hash=refresh_token_hash,
    )

    user_repository = MagicMock()
    user_repository.get_by_id.return_value = user

    auth_token_repository = MagicMock()
    auth_token_repository.get_active_revoked_access_by_jti.return_value = None
    auth_token_repository.get_active_by_hash.return_value = stored_refresh_token

    service = build_auth_service(
        user_repository=user_repository,
        auth_token_repository=auth_token_repository,
        jwt_service=jwt_service,
        token_service=token_service,
    )

    with pytest.raises(InvalidRefreshTokenError):
        service.logout(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    auth_token_repository.create.assert_not_called()
    auth_token_repository.revoke.assert_not_called()