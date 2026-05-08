import hashlib
import hmac
import secrets


class TokenService:
    def generate_secure_token(self) -> str:
        return secrets.token_urlsafe(64)

    def hash_token(self, token: str) -> str:
        if not token:
            raise ValueError("El token no puede estar vacio")

        return hashlib.sha256(
            token.encode("utf-8"),
        ).hexdigest()

    def verify_token_hash(
        self,
        token: str,
        token_hash: str,
    ) -> bool:
        if not token or not token_hash:
            return False

        calculated_hash = self.hash_token(token)

        return hmac.compare_digest(
            calculated_hash,
            token_hash,
        )