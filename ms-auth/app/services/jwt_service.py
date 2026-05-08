import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from uuid import UUID

import jwt
from jwt import ExpiredSignatureError
from jwt import InvalidTokenError as PyJWTInvalidTokenError

from app.core.config import settings
from app.models.enums import UserRole


class TokenExpiredError(Exception):
    pass


class TokenInvalidError(Exception):
    pass


class JWTService:
    def __init__(
        self,
        secret_key: Optional[str] = None,
        algorithm: Optional[str] = None,
        access_token_expire_minutes: Optional[int] = None,
    ) -> None:
        self.secret_key = secret_key or settings.jwt_secret_key
        self.algorithm = algorithm or settings.jwt_algorithm
        self.access_token_expire_minutes = (
            access_token_expire_minutes
            or settings.access_token_expire_minutes
        )

    def create_access_token(
        self,
        user_id: UUID,
        email: str,
        rol: UserRole,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        now = datetime.now(timezone.utc)

        if expires_delta is None:
            expires_delta = timedelta(
                minutes=self.access_token_expire_minutes,
            )

        expire_at = now + expires_delta

        payload = {
            "sub": str(user_id),
            "email": email,
            "rol": rol.value,
            "type": "access",
            "jti": str(uuid.uuid4()),
            "iat": now,
            "exp": expire_at,
        }

        return jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm,
        )

    def decode_token(self, token: str) -> Dict[str, Any]:
        try:
            return jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
            )
        except ExpiredSignatureError as exc:
            raise TokenExpiredError("Token expirado") from exc
        except PyJWTInvalidTokenError as exc:
            raise TokenInvalidError("Token invalido") from exc

    def validate_access_token(self, token: str) -> Dict[str, Any]:
        payload = self.decode_token(token)

        if payload.get("type") != "access":
            raise TokenInvalidError("El token no es un access token")

        required_claims = [
            "sub",
            "email",
            "rol",
            "jti",
            "type",
        ]

        for claim in required_claims:
            if claim not in payload:
                raise TokenInvalidError(
                    "El token no contiene los claims requeridos"
                )

        return payload