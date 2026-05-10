from uuid import uuid4

from app.grpc.auth_servicer import AuthServicer
from app.grpc.generated import auth_pb2
from app.services.auth_service import (
    AccessTokenExpiredError,
    InactiveUserError,
    InvalidAccessTokenError,
    InvalidUserIdentityDataError,
)


class FakeAuthService:
    def __init__(self) -> None:
        self.claims_result = None
        self.user_profile_result = None
        self.check_role_result = False
        self.identity_result = None
        self.error = None

    def validate_access_token_claims(self, access_token: str):
        if self.error is not None:
            raise self.error

        return self.claims_result

    def get_user_profile_by_id(self, user_id):
        return self.user_profile_result

    def check_user_role(self, user_id, role: str) -> bool:
        return self.check_role_result

    def create_or_get_user_identity(
        self,
        nombre_completo: str,
        email: str,
        role: str,
    ):
        if self.error is not None:
            raise self.error

        return self.identity_result


def build_servicer(fake_service: FakeAuthService) -> AuthServicer:
    return AuthServicer(
        auth_service_factory=lambda: fake_service,
    )


def build_user_profile() -> dict:
    return {
        "user_id": "00000000-0000-0000-0000-000000000001",
        "nombre_completo": "Usuario Test",
        "email": "usuario@agm.com",
        "rol": "ADMIN",
        "activo": True,
    }


def test_validate_token_returns_valid_claims() -> None:
    fake_service = FakeAuthService()
    fake_service.claims_result = {
        "user_id": "00000000-0000-0000-0000-000000000001",
        "email": "admin@agm.com",
        "role": "ADMIN",
        "jti": "jti-test",
        "activo": True,
    }

    servicer = build_servicer(fake_service)

    response = servicer.ValidateToken(
        auth_pb2.ValidateTokenRequest(token="access-token"),
        context=None,
    )

    assert response.valid is True
    assert response.claims.user_id == "00000000-0000-0000-0000-000000000001"
    assert response.claims.email == "admin@agm.com"
    assert response.claims.role == "ADMIN"
    assert response.claims.jti == "jti-test"
    assert response.claims.activo is True
    assert response.error_code == ""


def test_validate_token_returns_expired_error() -> None:
    fake_service = FakeAuthService()
    fake_service.error = AccessTokenExpiredError("Access token expirado")

    servicer = build_servicer(fake_service)

    response = servicer.ValidateToken(
        auth_pb2.ValidateTokenRequest(token="expired-token"),
        context=None,
    )

    assert response.valid is False
    assert response.error_code == "AUTH_ACCESS_TOKEN_EXPIRED"
    assert response.message == "Access token expirado"


def test_validate_token_returns_invalid_error() -> None:
    fake_service = FakeAuthService()
    fake_service.error = InvalidAccessTokenError("Access token invalido")

    servicer = build_servicer(fake_service)

    response = servicer.ValidateToken(
        auth_pb2.ValidateTokenRequest(token="invalid-token"),
        context=None,
    )

    assert response.valid is False
    assert response.error_code == "AUTH_INVALID_ACCESS_TOKEN"
    assert response.message == "Access token invalido"


def test_validate_token_returns_inactive_user_error() -> None:
    fake_service = FakeAuthService()
    fake_service.error = InactiveUserError("Usuario inactivo")

    servicer = build_servicer(fake_service)

    response = servicer.ValidateToken(
        auth_pb2.ValidateTokenRequest(token="access-token"),
        context=None,
    )

    assert response.valid is False
    assert response.error_code == "AUTH_INACTIVE_USER"
    assert response.message == "Usuario inactivo"


def test_get_user_by_id_returns_user_when_found() -> None:
    fake_service = FakeAuthService()
    fake_service.user_profile_result = build_user_profile()

    servicer = build_servicer(fake_service)

    response = servicer.GetUserById(
        auth_pb2.GetUserByIdRequest(
            user_id="00000000-0000-0000-0000-000000000001",
        ),
        context=None,
    )

    assert response.found is True
    assert response.user.email == "usuario@agm.com"
    assert response.user.role == "ADMIN"
    assert response.error_code == ""


def test_get_user_by_id_returns_not_found() -> None:
    fake_service = FakeAuthService()
    fake_service.user_profile_result = None

    servicer = build_servicer(fake_service)

    response = servicer.GetUserById(
        auth_pb2.GetUserByIdRequest(
            user_id="00000000-0000-0000-0000-000000000001",
        ),
        context=None,
    )

    assert response.found is False
    assert response.error_code == "AUTH_USER_NOT_FOUND"


def test_get_user_by_id_returns_invalid_user_id() -> None:
    fake_service = FakeAuthService()

    servicer = build_servicer(fake_service)

    response = servicer.GetUserById(
        auth_pb2.GetUserByIdRequest(
            user_id="invalid-uuid",
        ),
        context=None,
    )

    assert response.found is False
    assert response.error_code == "AUTH_INVALID_USER_ID"


def test_check_role_returns_allowed_true() -> None:
    fake_service = FakeAuthService()
    fake_service.check_role_result = True

    servicer = build_servicer(fake_service)

    response = servicer.CheckRole(
        auth_pb2.CheckRoleRequest(
            user_id=str(uuid4()),
            role="ADMIN",
        ),
        context=None,
    )

    assert response.allowed is True
    assert response.error_code == ""


def test_check_role_returns_allowed_false() -> None:
    fake_service = FakeAuthService()
    fake_service.check_role_result = False

    servicer = build_servicer(fake_service)

    response = servicer.CheckRole(
        auth_pb2.CheckRoleRequest(
            user_id=str(uuid4()),
            role="ADMIN",
        ),
        context=None,
    )

    assert response.allowed is False
    assert response.error_code == "AUTH_ROLE_NOT_ALLOWED"


def test_check_role_returns_invalid_user_id() -> None:
    fake_service = FakeAuthService()

    servicer = build_servicer(fake_service)

    response = servicer.CheckRole(
        auth_pb2.CheckRoleRequest(
            user_id="invalid-uuid",
            role="ADMIN",
        ),
        context=None,
    )

    assert response.allowed is False
    assert response.error_code == "AUTH_INVALID_USER_ID"


def test_create_or_get_user_identity_returns_created_user() -> None:
    fake_service = FakeAuthService()
    fake_service.identity_result = {
        "created": True,
        "user": build_user_profile(),
        "temporary_password": "temporary-password",
    }

    servicer = build_servicer(fake_service)

    response = servicer.CreateOrGetUserIdentity(
        auth_pb2.CreateOrGetUserIdentityRequest(
            nombre_completo="Usuario Test",
            email="usuario@agm.com",
            role="ADMIN",
        ),
        context=None,
    )

    assert response.created is True
    assert response.user.email == "usuario@agm.com"
    assert response.user.role == "ADMIN"
    assert response.temporary_password == "temporary-password"
    assert response.error_code == ""


def test_create_or_get_user_identity_returns_validation_error() -> None:
    fake_service = FakeAuthService()
    fake_service.error = InvalidUserIdentityDataError("Rol invalido")

    servicer = build_servicer(fake_service)

    response = servicer.CreateOrGetUserIdentity(
        auth_pb2.CreateOrGetUserIdentityRequest(
            nombre_completo="Usuario Test",
            email="usuario@agm.com",
            role="INVITADO",
        ),
        context=None,
    )

    assert response.created is False
    assert response.error_code == "AUTH_INVALID_USER_IDENTITY_DATA"
    assert response.message == "Rol invalido"