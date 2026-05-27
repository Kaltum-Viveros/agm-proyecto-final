from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.auth_token import AuthToken
from app.models.enums import TokenType, UserRole
from app.models.user import User
from app.repositories.auth_token_repository import AuthTokenRepository
from app.repositories.user_repository import UserRepository
from app.services.jwt_service import JWTService, TokenExpiredError, TokenInvalidError
from app.services.password_service import PasswordService
from app.services.rbac_service import RBACService
from app.services.token_service import TokenService
from app.grpc.clients.notificaciones_client import notificaciones_client


class InvalidCredentialsError(Exception):
    pass


class InactiveUserError(Exception):
    pass


class InvalidRefreshTokenError(Exception):
    pass


class InvalidAccessTokenError(Exception):
    pass


class AccessTokenExpiredError(Exception):
    pass


class InvalidPasswordResetTokenError(Exception):
    pass


class InvalidUserIdentityDataError(Exception):
    pass


class AuthService:
    def __init__(
        self,
        db: Optional[Session] = None,
        user_repository: Optional[UserRepository] = None,
        auth_token_repository: Optional[AuthTokenRepository] = None,
        password_service: Optional[PasswordService] = None,
        jwt_service: Optional[JWTService] = None,
        token_service: Optional[TokenService] = None,
        rbac_service: Optional[RBACService] = None,
    ) -> None:
        if user_repository is None or auth_token_repository is None:
            if db is None:
                raise ValueError(
                    "Se requiere una sesion de base de datos o repositorios"
                )

        self.user_repository = user_repository or UserRepository(db)
        self.auth_token_repository = (
            auth_token_repository or AuthTokenRepository(db)
        )
        self.password_service = password_service or PasswordService()
        self.jwt_service = jwt_service or JWTService()
        self.token_service = token_service or TokenService()
        self.rbac_service = rbac_service or RBACService()

    def login(
        self,
        email: str,
        contrasena: str,
    ) -> Dict[str, Any]:
        normalized_email = self._normalize_email(email)

        if not normalized_email or not contrasena:
            raise InvalidCredentialsError("Credenciales invalidas")

        user = self.user_repository.get_by_email(normalized_email)

        if user is None:
            raise InvalidCredentialsError("Credenciales invalidas")

        if not user.activo:
            raise InactiveUserError("Usuario inactivo")

        password_is_valid = self.password_service.verify_password(
            contrasena,
            user.contrasena_hash,
        )

        if not password_is_valid:
            raise InvalidCredentialsError("Credenciales invalidas")

        return self._create_session_response(user)

    def refresh_session(
        self,
        refresh_token: str,
    ) -> Dict[str, Any]:
        if not refresh_token:
            raise InvalidRefreshTokenError("Refresh token invalido")

        try:
            refresh_token_hash = self.token_service.hash_token(refresh_token)
        except ValueError as exc:
            raise InvalidRefreshTokenError("Refresh token invalido") from exc

        stored_token = self.auth_token_repository.get_active_by_hash(
            token_hash=refresh_token_hash,
            token_type=TokenType.REFRESH,
        )

        if stored_token is None:
            raise InvalidRefreshTokenError("Refresh token invalido")

        token_hash_is_valid = self.token_service.verify_token_hash(
            refresh_token,
            stored_token.token_hash,
        )

        if not token_hash_is_valid:
            raise InvalidRefreshTokenError("Refresh token invalido")

        if self._token_is_expired(stored_token):
            self.auth_token_repository.expire(stored_token)
            raise InvalidRefreshTokenError("Refresh token expirado")

        user = self.user_repository.get_by_id(stored_token.user_id)

        if user is None:
            self.auth_token_repository.revoke(stored_token)
            raise InvalidRefreshTokenError("Usuario no encontrado")

        if not user.activo:
            raise InactiveUserError("Usuario inactivo")

        self.auth_token_repository.mark_as_used(stored_token)

        return self._create_session_response(user)

    def get_current_user(
        self,
        access_token: str,
    ) -> Dict[str, Any]:
        payload = self._validate_active_access_token(access_token)
        user_id = self._get_user_id_from_payload(payload)

        user = self.user_repository.get_by_id(user_id)

        if user is None:
            raise InvalidAccessTokenError("Usuario no encontrado")

        if not user.activo:
            raise InactiveUserError("Usuario inactivo")

        return self._build_user_response(user)

    def validate_access_token_claims(
        self,
        access_token: str,
    ) -> Dict[str, Any]:
        payload = self._validate_active_access_token(access_token)
        user_id = self._get_user_id_from_payload(payload)

        user = self.user_repository.get_by_id(user_id)

        if user is None:
            raise InvalidAccessTokenError("Usuario no encontrado")

        if not user.activo:
            raise InactiveUserError("Usuario inactivo")

        return {
            "user_id": str(user.user_id),
            "email": user.email,
            "role": self._role_to_string(user.rol),
            "jti": str(payload["jti"]),
            "activo": user.activo,
        }

    def get_user_profile_by_id(
        self,
        user_id: UUID,
    ) -> Optional[Dict[str, Any]]:
        user = self.user_repository.get_by_id(user_id)

        if user is None:
            return None

        return self._build_user_response(user)

    def get_all_users(self) -> list[Dict[str, Any]]:
        users = self.user_repository.get_all()
        return [self._build_user_response(user) for user in users]

    def validate_current_user_roles(
        self,
        access_token: str,
        allowed_roles: Iterable[UserRole],
    ) -> Dict[str, Any]:
        current_user = self.get_current_user(access_token)

        return self.rbac_service.validate_user_role(
            current_user=current_user,
            allowed_roles=allowed_roles,
        )

    def check_user_role(
        self,
        user_id: UUID,
        role: str,
    ) -> bool:
        user = self.user_repository.get_by_id(user_id)

        if user is None:
            return False

        if not user.activo:
            return False

        return self.rbac_service.user_has_role(
            user_role=user.rol,
            allowed_roles=[role],
        )

    def create_or_get_user_identity(
        self,
        nombre_completo: str,
        email: str,
        role: str,
    ) -> Dict[str, Any]:
        normalized_name = self._normalize_name(nombre_completo)
        normalized_email = self._normalize_email(email)
        user_role = self._parse_user_role(role)

        if not normalized_name:
            raise InvalidUserIdentityDataError("Nombre requerido")

        if not normalized_email:
            raise InvalidUserIdentityDataError("Email requerido")

        existing_user = self.user_repository.get_by_email(normalized_email)

        if existing_user is not None:
            return {
                "created": False,
                "user": self._build_user_response(existing_user),
                "temporary_password": "",
            }

        temporary_password = self._generate_temporary_password()
        password_hash = self.password_service.hash_password(temporary_password)

        user = self.user_repository.create(
            nombre_completo=normalized_name,
            email=normalized_email,
            contrasena_hash=password_hash,
            rol=user_role,
            activo=True,
        )

        return {
            "created": True,
            "user": self._build_user_response(user),
            "temporary_password": temporary_password,
        }

    def logout(
        self,
        access_token: str,
        refresh_token: Optional[str] = None,
    ) -> Dict[str, bool]:
        payload = self._validate_active_access_token(access_token)
        user_id = self._get_user_id_from_payload(payload)

        user = self.user_repository.get_by_id(user_id)

        if user is None:
            raise InvalidAccessTokenError("Usuario no encontrado")

        if not user.activo:
            raise InactiveUserError("Usuario inactivo")

        refresh_token_to_revoke = None

        if refresh_token:
            refresh_token_to_revoke = self._get_valid_refresh_token_for_user(
                refresh_token=refresh_token,
                user_id=user.user_id,
            )

        access_token_expiration = self._get_expiration_from_payload(payload)

        self.auth_token_repository.create(
            user_id=user.user_id,
            token_type=TokenType.REVOKED_ACCESS,
            token_hash=None,
            jti=str(payload["jti"]),
            expiracion=access_token_expiration,
        )

        refresh_token_revoked = False

        if refresh_token_to_revoke is not None:
            self.auth_token_repository.revoke(refresh_token_to_revoke)
            refresh_token_revoked = True

        return {
            "logged_out": True,
            "access_token_revoked": True,
            "refresh_token_revoked": refresh_token_revoked,
        }

    def request_password_reset(
        self,
        email: str,
    ) -> Dict[str, Any]:
        reset_data = self.create_password_reset_token(email)

        if reset_data is None:
            return {
                "reset_requested": True,
                "reset_token": None,
            }

        # Disparamos el correo de recuperación vía gRPC
        try:
            notificaciones_client.enviar_reset_password(
                usuario_id=reset_data["user_id"],
                email=reset_data["email"],
                reset_token=reset_data["reset_token"]
            )
        except Exception as e:
            pass # No bloqueamos si falla la notificación

        token_to_return = None

        if settings.app_env.lower() == "development":
            token_to_return = reset_data["reset_token"]

        return {
            "reset_requested": True,
            "reset_token": token_to_return,
        }

    def create_password_reset_token(
        self,
        email: str,
    ) -> Optional[Dict[str, str]]:
        normalized_email = self._normalize_email(email)

        if not normalized_email:
            return None

        user = self.user_repository.get_by_email(normalized_email)

        if user is None or not user.activo:
            return None

        reset_token = self.token_service.generate_secure_token()
        reset_token_hash = self.token_service.hash_token(reset_token)
        reset_expires_at = self._get_password_reset_expiration()

        self.auth_token_repository.create(
            user_id=user.user_id,
            token_type=TokenType.PASSWORD_RESET,
            token_hash=reset_token_hash,
            jti=None,
            expiracion=reset_expires_at,
        )

        return {
            "user_id": str(user.user_id),
            "email": user.email,
            "reset_token": reset_token,
            "expires_at": reset_expires_at.isoformat(),
        }

    def reset_password(
        self,
        reset_token: str,
        nueva_contrasena: str,
    ) -> Dict[str, bool]:
        if not reset_token:
            raise InvalidPasswordResetTokenError("Token de recuperacion invalido")

        try:
            reset_token_hash = self.token_service.hash_token(reset_token)
        except ValueError as exc:
            raise InvalidPasswordResetTokenError(
                "Token de recuperacion invalido"
            ) from exc

        stored_token = self.auth_token_repository.get_active_by_hash(
            token_hash=reset_token_hash,
            token_type=TokenType.PASSWORD_RESET,
        )

        if stored_token is None:
            raise InvalidPasswordResetTokenError("Token de recuperacion invalido")

        token_hash_is_valid = self.token_service.verify_token_hash(
            reset_token,
            stored_token.token_hash,
        )

        if not token_hash_is_valid:
            raise InvalidPasswordResetTokenError("Token de recuperacion invalido")

        if self._token_is_expired(stored_token):
            self.auth_token_repository.expire(stored_token)
            raise InvalidPasswordResetTokenError("Token de recuperacion expirado")

        user = self.user_repository.get_by_id(stored_token.user_id)

        if user is None:
            self.auth_token_repository.revoke(stored_token)
            raise InvalidPasswordResetTokenError("Usuario no encontrado")

        if not user.activo:
            raise InactiveUserError("Usuario inactivo")

        new_password_hash = self.password_service.hash_password(nueva_contrasena)

        self.user_repository.update_password(
            user,
            new_password_hash,
        )

        self.auth_token_repository.mark_as_used(stored_token)

        return {
            "password_updated": True,
        }

    def _validate_active_access_token(
        self,
        access_token: str,
    ) -> Dict[str, Any]:
        if not access_token:
            raise InvalidAccessTokenError("Access token requerido")

        try:
            payload = self.jwt_service.validate_access_token(access_token)
        except TokenExpiredError as exc:
            raise AccessTokenExpiredError("Access token expirado") from exc
        except TokenInvalidError as exc:
            raise InvalidAccessTokenError("Access token invalido") from exc

        jti = payload.get("jti")

        if not jti:
            raise InvalidAccessTokenError("Access token invalido")

        revoked_token = self.auth_token_repository.get_active_revoked_access_by_jti(
            jti=str(jti),
        )

        if revoked_token is not None:
            raise InvalidAccessTokenError("Access token revocado")

        return payload

    def _get_valid_refresh_token_for_user(
        self,
        refresh_token: str,
        user_id: UUID,
    ) -> AuthToken:
        try:
            refresh_token_hash = self.token_service.hash_token(refresh_token)
        except ValueError as exc:
            raise InvalidRefreshTokenError("Refresh token invalido") from exc

        stored_token = self.auth_token_repository.get_active_by_hash(
            token_hash=refresh_token_hash,
            token_type=TokenType.REFRESH,
        )

        if stored_token is None:
            raise InvalidRefreshTokenError("Refresh token invalido")

        token_hash_is_valid = self.token_service.verify_token_hash(
            refresh_token,
            stored_token.token_hash,
        )

        if not token_hash_is_valid:
            raise InvalidRefreshTokenError("Refresh token invalido")

        if stored_token.user_id != user_id:
            raise InvalidRefreshTokenError("Refresh token invalido")

        if self._token_is_expired(stored_token):
            self.auth_token_repository.expire(stored_token)
            raise InvalidRefreshTokenError("Refresh token expirado")

        return stored_token

    def _create_session_response(
        self,
        user: User,
    ) -> Dict[str, Any]:
        access_token = self.jwt_service.create_access_token(
            user_id=user.user_id,
            email=user.email,
            rol=user.rol,
        )

        refresh_token = self.token_service.generate_secure_token()
        refresh_token_hash = self.token_service.hash_token(refresh_token)
        refresh_expires_at = self._get_refresh_expiration()

        self.auth_token_repository.create(
            user_id=user.user_id,
            token_type=TokenType.REFRESH,
            token_hash=refresh_token_hash,
            expiracion=refresh_expires_at,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
            "refresh_expires_at": refresh_expires_at,
            "user": self._build_user_response(user),
        }

    def _normalize_email(self, email: str) -> str:
        if email is None:
            return ""

        return email.strip().lower()

    def _normalize_name(self, name: str) -> str:
        if name is None:
            return ""

        return name.strip()

    def _parse_user_role(self, role: str) -> UserRole:
        normalized_role = self.rbac_service.normalize_role(role)

        try:
            return UserRole(normalized_role)
        except ValueError as exc:
            raise InvalidUserIdentityDataError("Rol invalido") from exc

    def _generate_temporary_password(self) -> str:
        return self.token_service.generate_secure_token()[:24]

    def _get_refresh_expiration(self) -> datetime:
        return datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days,
        )

    def _get_password_reset_expiration(self) -> datetime:
        return datetime.now(timezone.utc) + timedelta(
            minutes=settings.password_reset_token_expire_minutes,
        )

    def _token_is_expired(
        self,
        auth_token: AuthToken,
    ) -> bool:
        expiration = auth_token.expiracion

        if expiration.tzinfo is None:
            expiration = expiration.replace(tzinfo=timezone.utc)

        return expiration <= datetime.now(timezone.utc)

    def _get_user_id_from_payload(
        self,
        payload: Dict[str, Any],
    ) -> UUID:
        try:
            return UUID(str(payload.get("sub")))
        except ValueError as exc:
            raise InvalidAccessTokenError("Access token invalido") from exc
        except TypeError as exc:
            raise InvalidAccessTokenError("Access token invalido") from exc

    def _get_expiration_from_payload(
        self,
        payload: Dict[str, Any],
    ) -> datetime:
        expiration = payload.get("exp")

        if isinstance(expiration, datetime):
            if expiration.tzinfo is None:
                return expiration.replace(tzinfo=timezone.utc)

            return expiration

        if isinstance(expiration, int) or isinstance(expiration, float):
            return datetime.fromtimestamp(expiration, timezone.utc)

        try:
            return datetime.fromtimestamp(float(str(expiration)), timezone.utc)
        except ValueError as exc:
            raise InvalidAccessTokenError("Access token invalido") from exc
        except TypeError as exc:
            raise InvalidAccessTokenError("Access token invalido") from exc

    def _build_user_response(self, user: User) -> Dict[str, Any]:
        return {
            "user_id": str(user.user_id),
            "nombre_completo": user.nombre_completo,
            "email": user.email,
            "rol": self._role_to_string(user.rol),
            "activo": user.activo,
        }

    def _role_to_string(self, role: Any) -> str:
        if isinstance(role, UserRole):
            return role.value

        return str(role)
