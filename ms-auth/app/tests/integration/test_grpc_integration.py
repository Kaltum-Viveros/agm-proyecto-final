import os

import grpc
import httpx
import pytest

from app.grpc.generated import auth_pb2, auth_pb2_grpc


RUN_INTEGRATION_TESTS = (
    os.getenv("RUN_INTEGRATION_TESTS", "false").lower() == "true"
)

BASE_URL = os.getenv("MS_AUTH_BASE_URL", "http://localhost:8001")
GRPC_TARGET = os.getenv("MS_AUTH_GRPC_TARGET", "localhost:50051")
TEST_EMAIL = os.getenv("MS_AUTH_TEST_EMAIL", "admin@agm.com")
TEST_PASSWORD = os.getenv("MS_AUTH_TEST_PASSWORD", "Admin12345")


pytestmark = pytest.mark.skipif(
    not RUN_INTEGRATION_TESTS,
    reason=(
        "Pruebas de integracion desactivadas. "
        "Usa RUN_INTEGRATION_TESTS=true para ejecutarlas."
    ),
)


def get_access_token() -> str:
    with httpx.Client(
        base_url=BASE_URL,
        timeout=10.0,
    ) as client:
        response = client.post(
            "/auth/login",
            json={
                "email": TEST_EMAIL,
                "contrasena": TEST_PASSWORD,
            },
        )

        assert response.status_code == 200

        body = response.json()

        return body["data"]["access_token"]


def get_grpc_stub():
    channel = grpc.insecure_channel(GRPC_TARGET)

    grpc.channel_ready_future(channel).result(timeout=10)

    return auth_pb2_grpc.AuthServiceStub(channel), channel


def test_grpc_validate_token_and_get_user_by_id() -> None:
    access_token = get_access_token()
    stub, channel = get_grpc_stub()

    try:
        validate_response = stub.ValidateToken(
            auth_pb2.ValidateTokenRequest(
                token=access_token,
            )
        )

        assert validate_response.valid is True
        assert validate_response.error_code == ""
        assert validate_response.claims.email == TEST_EMAIL.lower()
        assert validate_response.claims.user_id
        assert validate_response.claims.role

        get_user_response = stub.GetUserById(
            auth_pb2.GetUserByIdRequest(
                user_id=validate_response.claims.user_id,
            )
        )

        assert get_user_response.found is True
        assert get_user_response.error_code == ""
        assert get_user_response.user.user_id == validate_response.claims.user_id
        assert get_user_response.user.email == TEST_EMAIL.lower()
        assert get_user_response.user.activo is True

    finally:
        channel.close()


def test_grpc_check_role_for_authenticated_user() -> None:
    access_token = get_access_token()
    stub, channel = get_grpc_stub()

    try:
        validate_response = stub.ValidateToken(
            auth_pb2.ValidateTokenRequest(
                token=access_token,
            )
        )

        assert validate_response.valid is True

        check_role_response = stub.CheckRole(
            auth_pb2.CheckRoleRequest(
                user_id=validate_response.claims.user_id,
                role=validate_response.claims.role,
            )
        )

        assert check_role_response.allowed is True
        assert check_role_response.error_code == ""

    finally:
        channel.close()


def test_grpc_create_or_get_user_identity_returns_existing_admin() -> None:
    stub, channel = get_grpc_stub()

    try:
        response = stub.CreateOrGetUserIdentity(
            auth_pb2.CreateOrGetUserIdentityRequest(
                nombre_completo="Administrador AGM",
                email=TEST_EMAIL,
                role="ADMIN",
            )
        )

        assert response.error_code == ""
        assert response.user.email == TEST_EMAIL.lower()
        assert response.user.role == "ADMIN"
        assert response.user.activo is True

    finally:
        channel.close()