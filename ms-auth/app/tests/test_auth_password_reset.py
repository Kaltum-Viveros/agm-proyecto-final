from fastapi.testclient import TestClient

from app.api.auth import get_auth_service
from app.main import app
from app.services.auth_service import (
    InactiveUserError,
    InvalidPasswordResetTokenError,
)

client = TestClient(app)


class FakeAuthService:
    def __init__(
        self,
        forgot_result=None,
        reset_result=None,
        error=None,
    ) -> None:
        self.forgot_result = forgot_result
        self.reset_result = reset_result
        self.error = error
        self.received_email = None
        self.received_reset_token = None
        self.received_new_password = None

    def request_password_reset(
        self,
        email: str,
    ):
        self.received_email = email

        if self.error is not None:
            raise self.error

        return self.forgot_result

    def reset_password(
        self,
        reset_token: str,
        nueva_contrasena: str,
    ):
        self.received_reset_token = reset_token
        self.received_new_password = nueva_contrasena

        if self.error is not None:
            raise self.error

        return self.reset_result


def clear_overrides() -> None:
    app.dependency_overrides.clear()


def test_forgot_password_endpoint_returns_success_response() -> None:
    fake_service = FakeAuthService(
        forgot_result={
            "reset_requested": True,
            "reset_token": "reset-token-development",
        },
    )

    app.dependency_overrides[get_auth_service] = lambda: fake_service

    response = client.post(
        "/auth/forgot-password",
        json={
            "email": "admin@correo.com",
        },
    )

    clear_overrides()

    assert response.status_code == 200

    body = response.json()

    assert fake_service.received_email == "admin@correo.com"
    assert body["success"] is True
    assert body["message"] == "Solicitud de recuperacion procesada"
    assert body["data"]["reset_requested"] is True
    assert body["data"]["reset_token"] == "reset-token-development"


def test_forgot_password_endpoint_returns_generic_success_for_unknown_email() -> None:
    fake_service = FakeAuthService(
        forgot_result={
            "reset_requested": True,
            "reset_token": None,
        },
    )

    app.dependency_overrides[get_auth_service] = lambda: fake_service

    response = client.post(
        "/auth/forgot-password",
        json={
            "email": "noexiste@correo.com",
        },
    )

    clear_overrides()

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["data"]["reset_requested"] is True
    assert body["data"]["reset_token"] is None


def test_reset_password_endpoint_returns_success_response() -> None:
    fake_service = FakeAuthService(
        reset_result={
            "password_updated": True,
        },
    )

    app.dependency_overrides[get_auth_service] = lambda: fake_service

    response = client.post(
        "/auth/reset-password",
        json={
            "reset_token": "valid-reset-token",
            "nueva_contrasena": "NewPassword123",
        },
    )

    clear_overrides()

    assert response.status_code == 200

    body = response.json()

    assert fake_service.received_reset_token == "valid-reset-token"
    assert fake_service.received_new_password == "NewPassword123"
    assert body["success"] is True
    assert body["message"] == "Contraseña actualizada correctamente"
    assert body["data"]["password_updated"] is True


def test_reset_password_endpoint_returns_401_for_invalid_token() -> None:
    fake_service = FakeAuthService(
        error=InvalidPasswordResetTokenError("Token invalido"),
    )

    app.dependency_overrides[get_auth_service] = lambda: fake_service

    response = client.post(
        "/auth/reset-password",
        json={
            "reset_token": "invalid-reset-token",
            "nueva_contrasena": "NewPassword123",
        },
    )

    clear_overrides()

    assert response.status_code == 401

    body = response.json()

    assert body["success"] is False
    assert body["message"] == "Token de recuperacion invalido"
    assert body["error_code"] == "AUTH_INVALID_PASSWORD_RESET_TOKEN"


def test_reset_password_endpoint_returns_403_for_inactive_user() -> None:
    fake_service = FakeAuthService(
        error=InactiveUserError("Usuario inactivo"),
    )

    app.dependency_overrides[get_auth_service] = lambda: fake_service

    response = client.post(
        "/auth/reset-password",
        json={
            "reset_token": "valid-reset-token",
            "nueva_contrasena": "NewPassword123",
        },
    )

    clear_overrides()

    assert response.status_code == 403

    body = response.json()

    assert body["success"] is False
    assert body["message"] == "Usuario inactivo"
    assert body["error_code"] == "AUTH_INACTIVE_USER"