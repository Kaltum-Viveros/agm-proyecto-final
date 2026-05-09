from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
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
from app.services.token_service import TokenService


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


class AuthService:
    def __init__(
        self,
        db: Optional[Session] = None,
        user_repository: Optional[UserRepository] = None,
        auth_token_repository: Optional[AuthTokenRepository] = None,
        password_service: Optional[PasswordService] = None,
        jwt_service: Optional[JWTService] = None,
        token_service: Optional[TokenService] = None,
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
            jti=jti,
        )

        if revoked_token is not None:
            raise InvalidAccessTokenError("Access token revocado")

        user_id = self._get_user_id_from_payload(payload)

        user = self.user_repository.get_by_id(user_id)

        if user is None:
            raise InvalidAccessTokenError("Usuario no encontrado")

        if not user.activo:
            raise InactiveUserError("Usuario inactivo")

        return self._build_user_response(user)

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

    def _get_refresh_expiration(self) -> datetime:
        return datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days,
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

    def _build_user_response(self, user: User) -> Dict[str, Any]:
        rol = user.rol.value if isinstance(user.rol, UserRole) else str(user.rol)

        return {
            "user_id": str(user.user_id),
            "nombre_completo": user.nombre_completo,
            "email": user.email,
            "rol": rol,
            "activo": user.activo,
        }