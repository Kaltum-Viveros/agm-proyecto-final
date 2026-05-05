from sqlalchemy import Boolean, DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base
from app.models.auth_token import AuthToken
from app.models.enums import TokenStatus, TokenType, UserRole
from app.models.user import User


def test_user_model_table_name() -> None:
    assert User.__tablename__ == "users"


def test_auth_token_model_table_name() -> None:
    assert AuthToken.__tablename__ == "auth_tokens"


def test_user_model_columns() -> None:
    columns = User.__table__.columns

    assert "user_id" in columns
    assert "nombre_completo" in columns
    assert "email" in columns
    assert "contrasena_hash" in columns
    assert "rol" in columns
    assert "activo" in columns


def test_auth_token_model_columns() -> None:
    columns = AuthToken.__table__.columns

    assert "auth_token_id" in columns
    assert "user_id" in columns
    assert "token_type" in columns
    assert "token_hash" in columns
    assert "jti" in columns
    assert "expiracion" in columns
    assert "estado" in columns
    assert "creacion" in columns


def test_user_model_column_types() -> None:
    assert isinstance(User.__table__.columns["user_id"].type, UUID)
    assert isinstance(User.__table__.columns["nombre_completo"].type, String)
    assert isinstance(User.__table__.columns["email"].type, String)
    assert isinstance(User.__table__.columns["contrasena_hash"].type, String)
    assert isinstance(User.__table__.columns["rol"].type, Enum)
    assert isinstance(User.__table__.columns["activo"].type, Boolean)


def test_auth_token_model_column_types() -> None:
    assert isinstance(AuthToken.__table__.columns["auth_token_id"].type, UUID)
    assert isinstance(AuthToken.__table__.columns["user_id"].type, UUID)
    assert isinstance(AuthToken.__table__.columns["token_type"].type, Enum)
    assert isinstance(AuthToken.__table__.columns["token_hash"].type, String)
    assert isinstance(AuthToken.__table__.columns["jti"].type, String)
    assert isinstance(AuthToken.__table__.columns["expiracion"].type, DateTime)
    assert isinstance(AuthToken.__table__.columns["estado"].type, Enum)
    assert isinstance(AuthToken.__table__.columns["creacion"].type, DateTime)


def test_user_model_constraints() -> None:
    columns = User.__table__.columns

    assert columns["user_id"].primary_key is True
    assert columns["nombre_completo"].nullable is False
    assert columns["email"].nullable is False
    assert columns["email"].unique is True
    assert columns["contrasena_hash"].nullable is False
    assert columns["rol"].nullable is False
    assert columns["activo"].nullable is False


def test_auth_token_model_constraints() -> None:
    columns = AuthToken.__table__.columns

    assert columns["auth_token_id"].primary_key is True
    assert columns["user_id"].nullable is False
    assert columns["token_type"].nullable is False
    assert columns["expiracion"].nullable is False
    assert columns["estado"].nullable is False
    assert columns["creacion"].nullable is False


def test_user_role_values() -> None:
    assert UserRole.ADMIN.value == "ADMIN"
    assert UserRole.DOCENTE.value == "DOCENTE"
    assert UserRole.ALUMNO.value == "ALUMNO"


def test_token_type_values() -> None:
    assert TokenType.REFRESH.value == "REFRESH"
    assert TokenType.PASSWORD_RESET.value == "PASSWORD_RESET"
    assert TokenType.REVOKED_ACCESS.value == "REVOKED_ACCESS"


def test_token_status_values() -> None:
    assert TokenStatus.ACTIVE.value == "ACTIVE"
    assert TokenStatus.USED.value == "USED"
    assert TokenStatus.REVOKED.value == "REVOKED"
    assert TokenStatus.EXPIRED.value == "EXPIRED"


def test_models_are_registered_in_base_metadata() -> None:
    assert "users" in Base.metadata.tables
    assert "auth_tokens" in Base.metadata.tables