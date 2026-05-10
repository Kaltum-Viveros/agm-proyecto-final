import os

import httpx
import pytest


RUN_INTEGRATION_TESTS = (
    os.getenv("RUN_INTEGRATION_TESTS", "false").lower() == "true"
)

BASE_URL = os.getenv("MS_AUTH_BASE_URL", "http://localhost:8001")
TEST_EMAIL = os.getenv("MS_AUTH_TEST_EMAIL", "admin@agm.com")
TEST_PASSWORD = os.getenv("MS_AUTH_TEST_PASSWORD", "Admin12345")


pytestmark = pytest.mark.skipif(
    not RUN_INTEGRATION_TESTS,
    reason=(
        "Pruebas de integracion desactivadas. "
        "Usa RUN_INTEGRATION_TESTS=true para ejecutarlas."
    ),
)


def test_rest_health_login_refresh_me_and_logout_flow() -> None:
    with httpx.Client(
        base_url=BASE_URL,
        timeout=10.0,
    ) as client:
        health_response = client.get("/health")

        assert health_response.status_code == 200

        health_body = health_response.json()

        assert health_body["success"] is True
        assert health_body["data"]["service"] == "ms-auth"
        assert health_body["data"]["status"] == "ok"

        login_response = client.post(
            "/auth/login",
            json={
                "email": TEST_EMAIL,
                "contrasena": TEST_PASSWORD,
            },
        )

        assert login_response.status_code == 200

        login_body = login_response.json()

        assert login_body["success"] is True
        assert login_body["message"] == "Login exitoso"

        access_token = login_body["data"]["access_token"]
        refresh_token = login_body["data"]["refresh_token"]

        assert access_token
        assert refresh_token

        me_response = client.get(
            "/auth/me",
            headers={
                "Authorization": "Bearer " + access_token,
            },
        )

        assert me_response.status_code == 200

        me_body = me_response.json()

        assert me_body["success"] is True
        assert me_body["data"]["email"] == TEST_EMAIL.lower()
        assert me_body["data"]["activo"] is True

        refresh_response = client.post(
            "/auth/refresh-token",
            json={
                "refresh_token": refresh_token,
            },
        )

        assert refresh_response.status_code == 200

        refresh_body = refresh_response.json()

        assert refresh_body["success"] is True
        assert refresh_body["message"] == "Sesion renovada correctamente"

        renewed_access_token = refresh_body["data"]["access_token"]
        renewed_refresh_token = refresh_body["data"]["refresh_token"]

        assert renewed_access_token
        assert renewed_refresh_token
        assert renewed_access_token != access_token
        assert renewed_refresh_token != refresh_token

        logout_response = client.post(
            "/auth/logout",
            headers={
                "Authorization": "Bearer " + renewed_access_token,
            },
            json={
                "refresh_token": renewed_refresh_token,
            },
        )

        assert logout_response.status_code == 200

        logout_body = logout_response.json()

        assert logout_body["success"] is True
        assert logout_body["message"] == "Logout exitoso"
        assert logout_body["data"]["logged_out"] is True
        assert logout_body["data"]["access_token_revoked"] is True
        assert logout_body["data"]["refresh_token_revoked"] is True

        revoked_me_response = client.get(
            "/auth/me",
            headers={
                "Authorization": "Bearer " + renewed_access_token,
            },
        )

        assert revoked_me_response.status_code == 401

        revoked_me_body = revoked_me_response.json()

        assert revoked_me_body["success"] is False
        assert revoked_me_body["error_code"] == "AUTH_INVALID_ACCESS_TOKEN"


def test_rest_forgot_password_returns_generic_success() -> None:
    with httpx.Client(
        base_url=BASE_URL,
        timeout=10.0,
    ) as client:
        response = client.post(
            "/auth/forgot-password",
            json={
                "email": TEST_EMAIL,
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["success"] is True
        assert body["message"] == "Solicitud de recuperacion procesada"
        assert body["data"]["reset_requested"] is True