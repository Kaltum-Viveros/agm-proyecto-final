from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.api.auth import get_auth_service
from app.main import app
from app.services.auth_service import InactiveUserError, InvalidCredentialsError

client = TestClient(app)


class FakeAuthService:
    def __init__(
        self,
        result=None,
        error=None,
    ) -> None:
        self.result = result
        self.error = error

    def login(
        self,
        email: str,
        contrasena: str,
    ):
        if self.error is not None:
            raise self.error

        return self.result


def build_login_result() -> dict:
    return {
        "access_token": "access-token",
        "refresh_token": "refresh-token",
        "token_type": "Bearer",
        "expires_in": 900,
        "refresh_expires_at": datetime.now(timezone.utc),
        "user": {
            "user_id": "00000000-0000-0000-0000-000000000001",
            "nombre_completo": "Usuario Test",
            "email": "admin@correo.com",
            "rol": "ADMIN",
            "activo": True,
        },
    }


def clear_overrides() -> None:
    app.dependency_overrides.clear()


def test_login_endpoint_returns_success_response() -> None:
    fake_service = FakeAuthService(
        result=build_login_result(),
    )

    app.dependency_overrides[get_auth_service] = lambda: fake_service

    response = client.post(
        "/auth/login",
        json={
            "email": "admin@correo.com",
            "contrasena": "Password123",
        },
    )

    clear_overrides()

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "Login exitoso"
    assert body["data"]["access_token"] == "access-token"
    assert body["data"]["refresh_token"] == "refresh-token"
    assert body["data"]["token_type"] == "Bearer"
    assert body["data"]["expires_in"] == 900
    assert body["data"]["user"]["email"] == "admin@correo.com"
    assert body["data"]["user"]["rol"] == "ADMIN"


def test_login_endpoint_returns_401_for_invalid_credentials() -> None:
    fake_service = FakeAuthService(
        error=InvalidCredentialsError("Credenciales invalidas"),
    )

    app.dependency_overrides[get_auth_service] = lambda: fake_service

    response = client.post(
        "/auth/login",
        json={
            "email": "admin@correo.com",
            "contrasena": "WrongPassword",
        },
    )

    clear_overrides()

    assert response.status_code == 401

    body = response.json()

    assert body["success"] is False
    assert body["message"] == "Credenciales invalidas"
    assert body["error_code"] == "AUTH_INVALID_CREDENTIALS"


def test_login_endpoint_returns_403_for_inactive_user() -> None:
    fake_service = FakeAuthService(
        error=InactiveUserError("Usuario inactivo"),
    )

    app.dependency_overrides[get_auth_service] = lambda: fake_service

    response = client.post(
        "/auth/login",
        json={
            "email": "admin@correo.com",
            "contrasena": "Password123",
        },
    )

    clear_overrides()

    assert response.status_code == 403

    body = response.json()

    assert body["success"] is False
    assert body["message"] == "Usuario inactivo"
    assert body["error_code"] == "AUTH_INACTIVE_USER"