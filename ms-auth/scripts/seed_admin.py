import sys
from pathlib import Path
from typing import Any, Dict

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

from app.core.config import settings  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.models.enums import UserRole  # noqa: E402
from app.models.user import User  # noqa: E402
from app.repositories.user_repository import UserRepository  # noqa: E402
from app.services.password_service import PasswordService  # noqa: E402


def normalize_email(email: str) -> str:
    if email is None:
        return ""

    return email.strip().lower()


def validate_seed_data(
    nombre_completo: str,
    email: str,
    password: str,
) -> None:
    if not nombre_completo or not nombre_completo.strip():
        raise ValueError("SEED_ADMIN_NAME no puede estar vacio")

    if not email or not email.strip():
        raise ValueError("SEED_ADMIN_EMAIL no puede estar vacio")

    if not password:
        raise ValueError("SEED_ADMIN_PASSWORD no puede estar vacio")

    if len(password) < 8:
        raise ValueError(
            "SEED_ADMIN_PASSWORD debe tener al menos 8 caracteres"
        )


def seed_admin_user(
    user_repository: UserRepository,
    password_service: PasswordService,
    nombre_completo: str,
    email: str,
    password: str,
) -> Dict[str, Any]:
    normalized_email = normalize_email(email)

    validate_seed_data(
        nombre_completo=nombre_completo,
        email=normalized_email,
        password=password,
    )

    existing_user = user_repository.get_by_email(normalized_email)

    if existing_user is not None:
        return {
            "created": False,
            "user": existing_user,
        }

    password_hash = password_service.hash_password(password)

    user = user_repository.create(
        nombre_completo=nombre_completo.strip(),
        email=normalized_email,
        contrasena_hash=password_hash,
        rol=UserRole.ADMIN,
        activo=True,
    )

    return {
        "created": True,
        "user": user,
    }


def run_seed() -> int:
    db = SessionLocal()

    try:
        user_repository = UserRepository(db)
        password_service = PasswordService()

        result = seed_admin_user(
            user_repository=user_repository,
            password_service=password_service,
            nombre_completo=settings.seed_admin_name,
            email=settings.seed_admin_email,
            password=settings.seed_admin_password,
        )

        user = result["user"]

        if result["created"]:
            print(
                "Usuario administrador creado correctamente: "
                + str(user.email)
            )
        else:
            print(
                "El usuario administrador ya existe: "
                + str(user.email)
            )

        return 0

    except Exception as exc:
        print(
            "Error al ejecutar seed de administrador: " + str(exc),
            file=sys.stderr,
        )
        return 1

    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(run_seed())