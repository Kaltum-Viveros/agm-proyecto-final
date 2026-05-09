from fastapi.testclient import TestClient

from app.api.auth import get_auth_service
from app.main import app
from app.services.auth_service import (
    AccessTokenExpiredError,
    InactiveUserError,
    InvalidAccessTokenError,
    InvalidRefreshTokenError,
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
        self.received_refresh_token = None

    def logout(
        self,
        access_token: str,
        refresh_token=None,
    ):
        self.received_access_token = access_token
        self.received_refresh_token = refresh_token

        if self.error is not None:
            raise self.error

        return self.result


def build_logout_result(
    refresh_token_revoked: bool = True,
) -> dict:
    return {
        "logged_out": True,
        "access_token_revoked": True,
        "refresh_token_revoked": refresh_token_revoked,
    }


def clear_overrides() -> None:
    app.dependency_overrides.clear()


def test_logout_endpoint_returns_success_response_with_refresh_token() -> None:
    fake_service = FakeAuthService(
        result=build_logout_result(refresh_token_revoked=True),
    )

    app.dependency_overrides[get_auth_service] = lambda: fake_service

    response = client.post(
        "/auth/logout",
        headers={
            "Authorization": "Bearer access-token",
        },
        json={
            "refresh_token": "refresh-token",
        },
    )

    clear_overrides()

    assert response.status_code == 200

    body = response.json()

    assert fake_service.received_access_token == "access-token"
    assert fake_service.received_refresh_token == "refresh-token"
    assert body["success"] is True
    assert body["message"] == "Logout exitoso"
    assert body["data"]["logged_out"] is True
    assert body["data"]["access_token_revoked"] is True
    assert body["data"]["refresh_token_revoked"] is True


def test_logout_endpoint_returns_success_response_without_refresh_token() -> None:
    fake_service = FakeAuthService(
        result=build_logout_result(refresh_token_revoked=False),
    )

    app.dependency_overrides[get_auth_service] = lambda: fake_service

    response = client.post(
        "/auth/logout",
        headers={
            "Authorization": "Bearer access-token",
        },
    )

    clear_overrides()

    assert response.status_code == 200

    body = response.json()

    assert fake_service.received_access_token == "access-token"
    assert fake_service.received_refresh_token is None
    assert body["success"] is True
    assert body["data"]["logged_out"] is True
    assert body["data"]["access_token_revoked"] is True
    assert body["data"]["refresh_token_revoked"] is False


def test_logout_endpoint_returns_401_for_missing_access_token() -> None:
    fake_service = FakeAuthService(
        error=InvalidAccessTokenError("Access token requerido"),
    )

    app.dependency_overrides[get_auth_service] = lambda: fake_service

    response = client.post("/auth/logout")

    clear_overrides()

    assert response.status_code == 401

    body = response.json()

    assert fake_service.received_access_token == ""
    assert body["success"] is False
    assert body["message"] == "Access token invalido"
    assert body["error_code"] == "AUTH_INVALID_ACCESS_TOKEN"


def test_logout_endpoint_returns_401_for_expired_access_token() -> None:
    fake_service = FakeAuthService(
        error=AccessTokenExpiredError("Access token expirado"),
    )

    app.dependency_overrides[get_auth_service] = lambda: fake_service

    response = client.post(
        "/auth/logout",
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


def test_logout_endpoint_returns_401_for_invalid_access_token() -> None:
    fake_service = FakeAuthService(
        error=InvalidAccessTokenError("Access token invalido"),
    )

    app.dependency_overrides[get_auth_service] = lambda: fake_service

    response = client.post(
        "/auth/logout",
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


def test_logout_endpoint_returns_401_for_invalid_refresh_token() -> None:
    fake_service = FakeAuthService(
        error=InvalidRefreshTokenError("Refresh token invalido"),
    )

    app.dependency_overrides[get_auth_service] = lambda: fake_service

    response = client.post(
        "/auth/logout",
        headers={
            "Authorization": "Bearer access-token",
        },
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


def test_logout_endpoint_returns_403_for_inactive_user() -> None:
    fake_service = FakeAuthService(
        error=InactiveUserError("Usuario inactivo"),
    )

    app.dependency_overrides[get_auth_service] = lambda: fake_service

    response = client.post(
        "/auth/logout",
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