from fastapi.testclient import TestClient

from app.api.auth import get_auth_service
from app.main import app
from app.services.auth_service import (
    AccessTokenExpiredError,
    InactiveUserError,
    InvalidAccessTokenError,
)

client = TestClient(app)


class FakeAuthService:
    def __init__(
        self,
        result=None,
        error=None,
    ) -> None:
        self.result = result
        self.error = error
        self.received_access_token = None

    def get_current_user(
        self,
        access_token: str,
    ):
        self.received_access_token = access_token

        if self.error is not None:
            raise self.error

        return self.result


def build_current_user_result() -> dict:
    return {
        "user_id": "00000000-0000-0000-0000-000000000001",
        "nombre_completo": "Usuario Test",
        "email": "admin@correo.com",
        "rol": "ADMIN",
        "activo": True,
    }


def clear_overrides() -> None:
    app.dependency_overrides.clear()


def test_me_endpoint_returns_authenticated_user() -> None:
    fake_service = FakeAuthService(
        result=build_current_user_result(),
    )

    app.dependency_overrides[get_auth_service] = lambda: fake_service

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": "Bearer access-token",
        },
    )

    clear_overrides()

    assert response.status_code == 200

    body = response.json()

    assert fake_service.received_access_token == "access-token"
    assert body["success"] is True
    assert body["message"] == "Usuario autenticado"
    assert body["data"]["email"] == "admin@correo.com"
    assert body["data"]["rol"] == "ADMIN"
    assert body["data"]["activo"] is True


def test_me_endpoint_returns_401_for_missing_access_token() -> None:
    fake_service = FakeAuthService(
        error=InvalidAccessTokenError("Access token requerido"),
    )

    app.dependency_overrides[get_auth_service] = lambda: fake_service

    response = client.get("/auth/me")

    clear_overrides()

    assert response.status_code == 401

    body = response.json()

    assert fake_service.received_access_token == ""
    assert body["success"] is False
    assert body["message"] == "Access token invalido"
    assert body["error_code"] == "AUTH_INVALID_ACCESS_TOKEN"


def test_me_endpoint_returns_401_for_invalid_access_token() -> None:
    fake_service = FakeAuthService(
        error=InvalidAccessTokenError("Access token invalido"),
    )

    app.dependency_overrides[get_auth_service] = lambda: fake_service

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    clear_overrides()

    assert response.status_code == 401

    body = response.json()

    assert body["success"] is False
    assert body["message"] == "Access token invalido"
    assert body["error_code"] == "AUTH_INVALID_ACCESS_TOKEN"


def test_me_endpoint_returns_401_for_expired_access_token() -> None:
    fake_service = FakeAuthService(
        error=AccessTokenExpiredError("Access token expirado"),
    )

    app.dependency_overrides[get_auth_service] = lambda: fake_service

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": "Bearer expired-token",
        },
    )

    clear_overrides()

    assert response.status_code == 401

    body = response.json()

    assert body["success"] is False
    assert body["message"] == "Access token expirado"
    assert body["error_code"] == "AUTH_ACCESS_TOKEN_EXPIRED"


def test_me_endpoint_returns_403_for_inactive_user() -> None:
    fake_service = FakeAuthService(
        error=InactiveUserError("Usuario inactivo"),
    )

    app.dependency_overrides[get_auth_service] = lambda: fake_service

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": "Bearer access-token",
        },
    )

    clear_overrides()

    assert response.status_code == 403

    body = response.json()

    assert body["success"] is False
    assert body["message"] == "Usuario inactivo"
    assert body["error_code"] == "AUTH_INACTIVE_USER"