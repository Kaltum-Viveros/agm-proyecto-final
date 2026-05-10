from typing import Any, Dict, Iterable, List

from app.models.enums import UserRole


class ForbiddenRoleError(Exception):
    pass


class RBACService:
    def normalize_role(
        self,
        role: Any,
    ) -> str:
        if isinstance(role, UserRole):
            return role.value

        return str(role).strip().upper()

    def normalize_roles(
        self,
        roles: Iterable[Any],
    ) -> List[str]:
        return [
            self.normalize_role(role)
            for role in roles
        ]

    def user_has_role(
        self,
        user_role: Any,
        allowed_roles: Iterable[Any],
    ) -> bool:
        normalized_user_role = self.normalize_role(user_role)
        normalized_allowed_roles = self.normalize_roles(allowed_roles)

        return normalized_user_role in normalized_allowed_roles

    def validate_user_role(
        self,
        current_user: Dict[str, Any],
        allowed_roles: Iterable[Any],
    ) -> Dict[str, Any]:
        normalized_allowed_roles = self.normalize_roles(allowed_roles)

        if not normalized_allowed_roles:
            raise ForbiddenRoleError("No hay roles permitidos configurados")

        user_role = current_user.get("rol")

        if not self.user_has_role(
            user_role=user_role,
            allowed_roles=normalized_allowed_roles,
        ):
            raise ForbiddenRoleError("Rol no autorizado")

        return current_user