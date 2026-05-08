from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.enums import TokenType, UserRole
from app.models.user import User
from app.repositories.auth_token_repository import AuthTokenRepository
from app.repositories.user_repository import UserRepository
from app.services.jwt_service import JWTService
from app.services.password_service import PasswordService
from app.services.token_service import TokenService


class InvalidCredentialsError(Exception):
    pass


class InactiveUserError(Exception):
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

    def _build_user_response(self, user: User) -> Dict[str, Any]:
        rol = user.rol.value if isinstance(user.rol, UserRole) else str(user.rol)

        return {
            "user_id": str(user.user_id),
            "nombre_completo": user.nombre_completo,
            "email": user.email,
            "rol": rol,
            "activo": user.activo,
        }