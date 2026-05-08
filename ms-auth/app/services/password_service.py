from passlib.context import CryptContext


password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


class PasswordService:
    def hash_password(self, plain_password: str) -> str:
        if not plain_password:
            raise ValueError("La contrasena no puede estar vacia")

        return password_context.hash(plain_password)

    def verify_password(
        self,
        plain_password: str,
        hashed_password: str,
    ) -> bool:
        if not plain_password or not hashed_password:
            return False

        try:
            return password_context.verify(
                plain_password,
                hashed_password,
            )
        except ValueError:
            return False