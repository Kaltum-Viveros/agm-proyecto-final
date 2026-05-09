from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.api.auth import get_auth_service
from app.main import app
from app.services.auth_service import InactiveUserError, InvalidRefreshTokenError

client = TestClient(app)


class FakeAuthService:
    def __init__(
        self,
        result=None,
        error=None,
    ) -> None:
        self.result = result
        self.error = error

    def refresh_session(
        self,
        refresh_token: str,
    ):
        if self.error is not None:
            raise self.error

        return self.result


def build_refresh_result() -> dict:
    return {
        "access_token": "new-access-token",
        "refresh_token": "new-refresh-token",
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


def test_refresh_token_endpoint_returns_success_response() -> None:
    fake_service = FakeAuthService(
        result=build_refresh_result(),
    )

    app.dependency_overrides[get_auth_service] = lambda: fake_service

    response = client.post(
        "/auth/refresh-token",
        json={
            "refresh_token": "valid-refresh-token",
        },
    )

    clear_overrides()

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "Sesion renovada correctamente"
    assert body["data"]["access_token"] == "new-access-token"
    assert body["data"]["refresh_token"] == "new-refresh-token"
    assert body["data"]["token_type"] == "Bearer"
    assert body["data"]["expires_in"] == 900
    assert body["data"]["user"]["email"] == "admin@correo.com"
    assert body["data"]["user"]["rol"] == "ADMIN"


def test_refresh_token_endpoint_returns_401_for_invalid_refresh_token() -> None:
    fake_service = FakeAuthService(
        error=InvalidRefreshTokenError("Refresh token invalido"),
    )

    app.dependency_overrides[get_auth_service] = lambda: fake_service

    response = client.post(
        "/auth/refresh-token",
        json={
            "refresh_token": "invalid-refresh-token",
        },
    )

    clear_overrides()

    assert response.status_code == 401

    body = response.json()

    assert body["success"] is False
    assert body["message"] == "Refresh token invalido"
    assert body["error_code"] == "AUTH_INVALID_REFRESH_TOKEN"


def test_refresh_token_endpoint_returns_403_for_inactive_user() -> None:
    fake_service = FakeAuthService(
        error=InactiveUserError("Usuario inactivo"),
    )

    app.dependency_overrides[get_auth_service] = lambda: fake_service

    response = client.post(
        "/auth/refresh-token",
        json={
            "refresh_token": "valid-refresh-token",
        },
    )

    clear_overrides()

    assert response.status_code == 403

    body = response.json()

    assert body["success"] is False
    assert body["message"] == "Usuario inactivo"
    assert body["error_code"] == "AUTH_INACTIVE_USER"