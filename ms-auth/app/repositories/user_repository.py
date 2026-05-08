from typing import Optional
from uuid import UUID

from app.models.enums import UserRole
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    def get_by_id(self, user_id: UUID) -> Optional[User]:
        return (
            self.db.query(User)
            .filter(User.user_id == user_id)
            .first()
        )

    def get_by_email(self, email: str) -> Optional[User]:
        return (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )

    def create(
        self,
        nombre_completo: str,
        email: str,
        contrasena_hash: str,
        rol: UserRole,
        activo: bool = True,
    ) -> User:
        user = User(
            nombre_completo=nombre_completo,
            email=email,
            contrasena_hash=contrasena_hash,
            rol=rol,
            activo=activo,
        )

        return self.save(user)

    def update_password(
        self,
        user: User,
        contrasena_hash: str,
    ) -> User:
        user.contrasena_hash = contrasena_hash

        return self.commit_changes(user)

    def set_active(
        self,
        user: User,
        activo: bool,
    ) -> User:
        user.activo = activo

        return self.commit_changes(user)