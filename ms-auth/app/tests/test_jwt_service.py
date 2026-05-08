from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import pytest

from app.models.enums import UserRole
from app.services.jwt_service import (
    JWTService,
    TokenExpiredError,
    TokenInvalidError,
)


def test_create_access_token_returns_string() -> None:
    service = JWTService()

    token = service.create_access_token(
        user_id=uuid4(),
        email="admin@correo.com",
        rol=UserRole.ADMIN,
    )

    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_token_returns_expected_payload() -> None:
    service = JWTService()
    user_id = uuid4()

    token = service.create_access_token(
        user_id=user_id,
        email="admin@correo.com",
        rol=UserRole.ADMIN,
    )

    payload = service.decode_token(token)

    assert payload["sub"] == str(user_id)
    assert payload["email"] == "admin@correo.com"
    assert payload["rol"] == UserRole.ADMIN.value
    assert payload["type"] == "access"
    assert "jti" in payload
    assert "iat" in payload
    assert "exp" in payload


def test_validate_access_token_returns_payload() -> None:
    service = JWTService()
    user_id = uuid4()

    token = service.create_access_token(
        user_id=user_id,
        email="docente@correo.com",
        rol=UserRole.DOCENTE,
    )

    payload = service.validate_access_token(token)

    assert payload["sub"] == str(user_id)
    assert payload["email"] == "docente@correo.com"
    assert payload["rol"] == UserRole.DOCENTE.value
    assert payload["type"] == "access"


def test_decode_token_raises_error_for_expired_token() -> None:
    service = JWTService()

    token = service.create_access_token(
        user_id=uuid4(),
        email="alumno@correo.com",
        rol=UserRole.ALUMNO,
        expires_delta=timedelta(minutes=-1),
    )

    with pytest.raises(TokenExpiredError):
        service.decode_token(token)


def test_decode_token_raises_error_for_invalid_token() -> None:
    service = JWTService()

    with pytest.raises(TokenInvalidError):
        service.decode_token("invalid.token.value")


def test_validate_access_token_rejects_non_access_token() -> None:
    service = JWTService()

    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(uuid4()),
        "email": "admin@correo.com",
        "rol": UserRole.ADMIN.value,
        "type": "refresh",
        "jti": "test-jti",
        "iat": now,
        "exp": now + timedelta(minutes=15),
    }

    token = jwt.encode(
        payload,
        service.secret_key,
        algorithm=service.algorithm,
    )

    with pytest.raises(TokenInvalidError):
        service.validate_access_token(token)


def test_validate_access_token_rejects_token_without_required_claims() -> None:
    service = JWTService()

    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(uuid4()),
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=15),
    }

    token = jwt.encode(
        payload,
        service.secret_key,
        algorithm=service.algorithm,
    )

    with pytest.raises(TokenInvalidError):
        service.validate_access_token(token)