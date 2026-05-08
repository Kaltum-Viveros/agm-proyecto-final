from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.models.auth_token import AuthToken
from app.models.enums import TokenStatus, TokenType, UserRole
from app.models.user import User
from app.repositories.auth_token_repository import AuthTokenRepository
from app.repositories.user_repository import UserRepository


def create_mock_session() -> MagicMock:
    return MagicMock(spec=Session)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def test_user_repository_get_by_id_returns_user() -> None:
    db = create_mock_session()
    expected_user = User(
        nombre_completo="Usuario Test",
        email="test@correo.com",
        contrasena_hash="hash",
        rol=UserRole.ADMIN,
        activo=True,
    )

    db.query.return_value.filter.return_value.first.return_value = expected_user

    repository = UserRepository(db)
    result = repository.get_by_id(uuid4())

    assert result == expected_user
    db.query.assert_called_once_with(User)
    db.query.return_value.filter.assert_called_once()
    db.query.return_value.filter.return_value.first.assert_called_once()


def test_user_repository_get_by_email_returns_user() -> None:
    db = create_mock_session()
    expected_user = User(
        nombre_completo="Usuario Test",
        email="test@correo.com",
        contrasena_hash="hash",
        rol=UserRole.ADMIN,
        activo=True,
    )

    db.query.return_value.filter.return_value.first.return_value = expected_user

    repository = UserRepository(db)
    result = repository.get_by_email("test@correo.com")

    assert result == expected_user
    db.query.assert_called_once_with(User)
    db.query.return_value.filter.assert_called_once()
    db.query.return_value.filter.return_value.first.assert_called_once()


def test_user_repository_create_persists_user() -> None:
    db = create_mock_session()
    repository = UserRepository(db)

    result = repository.create(
        nombre_completo="Usuario Test",
        email="test@correo.com",
        contrasena_hash="hash",
        rol=UserRole.ADMIN,
    )

    created_user = db.add.call_args[0][0]

    assert result == created_user
    assert created_user.nombre_completo == "Usuario Test"
    assert created_user.email == "test@correo.com"
    assert created_user.contrasena_hash == "hash"
    assert created_user.rol == UserRole.ADMIN
    assert created_user.activo is True

    db.add.assert_called_once_with(created_user)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(created_user)


def test_user_repository_update_password_commits_changes() -> None:
    db = create_mock_session()
    repository = UserRepository(db)

    user = User(
        nombre_completo="Usuario Test",
        email="test@correo.com",
        contrasena_hash="old_hash",
        rol=UserRole.ADMIN,
        activo=True,
    )

    result = repository.update_password(user, "new_hash")

    assert result == user
    assert user.contrasena_hash == "new_hash"
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(user)


def test_user_repository_set_active_commits_changes() -> None:
    db = create_mock_session()
    repository = UserRepository(db)

    user = User(
        nombre_completo="Usuario Test",
        email="test@correo.com",
        contrasena_hash="hash",
        rol=UserRole.ADMIN,
        activo=True,
    )

    result = repository.set_active(user, False)

    assert result == user
    assert user.activo is False
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(user)


def test_user_repository_rolls_back_when_create_fails() -> None:
    db = create_mock_session()
    db.commit.side_effect = RuntimeError("commit failed")

    repository = UserRepository(db)

    with pytest.raises(RuntimeError):
        repository.create(
            nombre_completo="Usuario Test",
            email="test@correo.com",
            contrasena_hash="hash",
            rol=UserRole.ADMIN,
        )

    db.rollback.assert_called_once()


def test_auth_token_repository_get_by_id_returns_token() -> None:
    db = create_mock_session()
    expected_token = AuthToken(
        user_id=uuid4(),
        token_type=TokenType.REFRESH,
        token_hash="token_hash",
        expiracion=utc_now() + timedelta(days=7),
        estado=TokenStatus.ACTIVE,
    )

    db.query.return_value.filter.return_value.first.return_value = expected_token

    repository = AuthTokenRepository(db)
    result = repository.get_by_id(uuid4())

    assert result == expected_token
    db.query.assert_called_once_with(AuthToken)
    db.query.return_value.filter.assert_called_once()
    db.query.return_value.filter.return_value.first.assert_called_once()


def test_auth_token_repository_get_active_by_hash_returns_token() -> None:
    db = create_mock_session()
    expected_token = AuthToken(
        user_id=uuid4(),
        token_type=TokenType.REFRESH,
        token_hash="token_hash",
        expiracion=utc_now() + timedelta(days=7),
        estado=TokenStatus.ACTIVE,
    )

    db.query.return_value.filter.return_value.first.return_value = expected_token

    repository = AuthTokenRepository(db)
    result = repository.get_active_by_hash(
        token_hash="token_hash",
        token_type=TokenType.REFRESH,
    )

    assert result == expected_token
    db.query.assert_called_once_with(AuthToken)
    db.query.return_value.filter.assert_called_once()
    db.query.return_value.filter.return_value.first.assert_called_once()


def test_auth_token_repository_get_active_revoked_access_by_jti_returns_token() -> None:
    db = create_mock_session()
    expected_token = AuthToken(
        user_id=uuid4(),
        token_type=TokenType.REVOKED_ACCESS,
        jti="jwt-id",
        expiracion=utc_now() + timedelta(minutes=15),
        estado=TokenStatus.ACTIVE,
    )

    db.query.return_value.filter.return_value.first.return_value = expected_token

    repository = AuthTokenRepository(db)
    result = repository.get_active_revoked_access_by_jti("jwt-id")

    assert result == expected_token
    db.query.assert_called_once_with(AuthToken)
    db.query.return_value.filter.assert_called_once()
    db.query.return_value.filter.return_value.first.assert_called_once()


def test_auth_token_repository_list_active_by_user_returns_tokens() -> None:
    db = create_mock_session()
    expected_tokens = [
        AuthToken(
            user_id=uuid4(),
            token_type=TokenType.REFRESH,
            token_hash="token_hash",
            expiracion=utc_now() + timedelta(days=7),
            estado=TokenStatus.ACTIVE,
        )
    ]

    db.query.return_value.filter.return_value.all.return_value = expected_tokens

    repository = AuthTokenRepository(db)
    result = repository.list_active_by_user(
        user_id=uuid4(),
        token_type=TokenType.REFRESH,
    )

    assert result == expected_tokens
    db.query.assert_called_once_with(AuthToken)
    db.query.return_value.filter.assert_called_once()
    db.query.return_value.filter.return_value.all.assert_called_once()


def test_auth_token_repository_create_persists_token() -> None:
    db = create_mock_session()
    repository = AuthTokenRepository(db)

    user_id = uuid4()
    expiration = utc_now() + timedelta(days=7)

    result = repository.create(
        user_id=user_id,
        token_type=TokenType.REFRESH,
        token_hash="token_hash",
        expiracion=expiration,
    )

    created_token = db.add.call_args[0][0]

    assert result == created_token
    assert created_token.user_id == user_id
    assert created_token.token_type == TokenType.REFRESH
    assert created_token.token_hash == "token_hash"
    assert created_token.jti is None
    assert created_token.expiracion == expiration
    assert created_token.estado == TokenStatus.ACTIVE

    db.add.assert_called_once_with(created_token)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(created_token)


def test_auth_token_repository_create_revoked_access_token_with_jti() -> None:
    db = create_mock_session()
    repository = AuthTokenRepository(db)

    user_id = uuid4()
    expiration = utc_now() + timedelta(minutes=15)

    result = repository.create(
        user_id=user_id,
        token_type=TokenType.REVOKED_ACCESS,
        jti="jwt-id",
        expiracion=expiration,
    )

    created_token = db.add.call_args[0][0]

    assert result == created_token
    assert created_token.user_id == user_id
    assert created_token.token_type == TokenType.REVOKED_ACCESS
    assert created_token.token_hash is None
    assert created_token.jti == "jwt-id"
    assert created_token.expiracion == expiration
    assert created_token.estado == TokenStatus.ACTIVE

    db.add.assert_called_once_with(created_token)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(created_token)


def test_auth_token_repository_mark_as_used_commits_changes() -> None:
    db = create_mock_session()
    repository = AuthTokenRepository(db)

    auth_token = AuthToken(
        user_id=uuid4(),
        token_type=TokenType.PASSWORD_RESET,
        token_hash="token_hash",
        expiracion=utc_now() + timedelta(minutes=10),
        estado=TokenStatus.ACTIVE,
    )

    result = repository.mark_as_used(auth_token)

    assert result == auth_token
    assert auth_token.estado == TokenStatus.USED
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(auth_token)


def test_auth_token_repository_revoke_commits_changes() -> None:
    db = create_mock_session()
    repository = AuthTokenRepository(db)

    auth_token = AuthToken(
        user_id=uuid4(),
        token_type=TokenType.REFRESH,
        token_hash="token_hash",
        expiracion=utc_now() + timedelta(days=7),
        estado=TokenStatus.ACTIVE,
    )

    result = repository.revoke(auth_token)

    assert result == auth_token
    assert auth_token.estado == TokenStatus.REVOKED
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(auth_token)


def test_auth_token_repository_expire_commits_changes() -> None:
    db = create_mock_session()
    repository = AuthTokenRepository(db)

    auth_token = AuthToken(
        user_id=uuid4(),
        token_type=TokenType.REFRESH,
        token_hash="token_hash",
        expiracion=utc_now() - timedelta(days=1),
        estado=TokenStatus.ACTIVE,
    )

    result = repository.expire(auth_token)

    assert result == auth_token
    assert auth_token.estado == TokenStatus.EXPIRED
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(auth_token)


def test_auth_token_repository_rolls_back_when_create_fails() -> None:
    db = create_mock_session()
    db.commit.side_effect = RuntimeError("commit failed")

    repository = AuthTokenRepository(db)

    with pytest.raises(RuntimeError):
        repository.create(
            user_id=uuid4(),
            token_type=TokenType.REFRESH,
            token_hash="token_hash",
            expiracion=utc_now() + timedelta(days=7),
        )

    db.rollback.assert_called_once()