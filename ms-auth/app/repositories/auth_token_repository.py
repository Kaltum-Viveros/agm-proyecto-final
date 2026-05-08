from datetime import datetime
from typing import List, Optional
from uuid import UUID

from app.models.auth_token import AuthToken
from app.models.enums import TokenStatus, TokenType
from app.repositories.base import BaseRepository


class AuthTokenRepository(BaseRepository):
    def get_by_id(self, auth_token_id: UUID) -> Optional[AuthToken]:
        return (
            self.db.query(AuthToken)
            .filter(AuthToken.auth_token_id == auth_token_id)
            .first()
        )

    def get_active_by_hash(
        self,
        token_hash: str,
        token_type: TokenType,
    ) -> Optional[AuthToken]:
        return (
            self.db.query(AuthToken)
            .filter(
                AuthToken.token_hash == token_hash,
                AuthToken.token_type == token_type,
                AuthToken.estado == TokenStatus.ACTIVE,
            )
            .first()
        )

    def get_active_revoked_access_by_jti(
        self,
        jti: str,
    ) -> Optional[AuthToken]:
        return (
            self.db.query(AuthToken)
            .filter(
                AuthToken.jti == jti,
                AuthToken.token_type == TokenType.REVOKED_ACCESS,
                AuthToken.estado == TokenStatus.ACTIVE,
            )
            .first()
        )

    def list_active_by_user(
        self,
        user_id: UUID,
        token_type: TokenType,
    ) -> List[AuthToken]:
        return (
            self.db.query(AuthToken)
            .filter(
                AuthToken.user_id == user_id,
                AuthToken.token_type == token_type,
                AuthToken.estado == TokenStatus.ACTIVE,
            )
            .all()
        )

    def create(
        self,
        user_id: UUID,
        token_type: TokenType,
        expiracion: datetime,
        token_hash: Optional[str] = None,
        jti: Optional[str] = None,
        estado: TokenStatus = TokenStatus.ACTIVE,
    ) -> AuthToken:
        auth_token = AuthToken(
            user_id=user_id,
            token_type=token_type,
            token_hash=token_hash,
            jti=jti,
            expiracion=expiracion,
            estado=estado,
        )

        return self.save(auth_token)

    def mark_as_used(
        self,
        auth_token: AuthToken,
    ) -> AuthToken:
        auth_token.estado = TokenStatus.USED

        return self.commit_changes(auth_token)

    def revoke(
        self,
        auth_token: AuthToken,
    ) -> AuthToken:
        auth_token.estado = TokenStatus.REVOKED

        return self.commit_changes(auth_token)

    def expire(
        self,
        auth_token: AuthToken,
    ) -> AuthToken:
        auth_token.estado = TokenStatus.EXPIRED

        return self.commit_changes(auth_token)