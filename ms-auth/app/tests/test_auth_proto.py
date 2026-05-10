from pathlib import Path

from app.grpc.generated import auth_pb2, auth_pb2_grpc


REPO_ROOT = Path(__file__).resolve().parents[3]
PROTO_FILE = REPO_ROOT / "proto" / "auth.proto"


def test_auth_proto_file_exists() -> None:
    assert PROTO_FILE.exists()


def test_auth_proto_defines_auth_service() -> None:
    content = PROTO_FILE.read_text(encoding="utf-8")

    assert "service AuthService" in content


def test_auth_proto_defines_required_rpc_methods() -> None:
    content = PROTO_FILE.read_text(encoding="utf-8")

    assert "rpc ValidateToken" in content
    assert "rpc GetUserById" in content
    assert "rpc CheckRole" in content
    assert "rpc CreateOrGetUserIdentity" in content


def test_generated_auth_pb2_can_create_validate_token_request() -> None:
    request = auth_pb2.ValidateTokenRequest(
        token="access-token-test",
    )

    assert request.token == "access-token-test"


def test_generated_auth_pb2_can_create_user_profile() -> None:
    user = auth_pb2.UserProfile(
        user_id="00000000-0000-0000-0000-000000000001",
        nombre_completo="Usuario Test",
        email="usuario@agm.com",
        role="ADMIN",
        activo=True,
    )

    assert user.user_id == "00000000-0000-0000-0000-000000000001"
    assert user.nombre_completo == "Usuario Test"
    assert user.email == "usuario@agm.com"
    assert user.role == "ADMIN"
    assert user.activo is True


def test_generated_auth_service_has_expected_methods() -> None:
    service_descriptor = auth_pb2.DESCRIPTOR.services_by_name["AuthService"]
    method_names = set(service_descriptor.methods_by_name.keys())

    assert method_names == {
        "ValidateToken",
        "GetUserById",
        "CheckRole",
        "CreateOrGetUserIdentity",
    }


def test_generated_auth_pb2_grpc_has_servicer_class() -> None:
    assert hasattr(auth_pb2_grpc, "AuthServiceServicer")
    assert hasattr(auth_pb2_grpc, "AuthServiceStub")
    assert hasattr(auth_pb2_grpc, "add_AuthServiceServicer_to_server")