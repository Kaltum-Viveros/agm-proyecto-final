import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

from app.db.session import SessionLocal
from app.models.enums import UserRole
from app.repositories.user_repository import UserRepository
from app.services.password_service import PasswordService

def seed_test_users() -> int:
    db = SessionLocal()
    try:
        user_repo = UserRepository(db)
        pwd_service = PasswordService()

        users_to_create = [
            {
                "email": "docente@agm.com",
                "nombre_completo": "Docente de Prueba",
                "password": "password123",
                "rol": UserRole.DOCENTE
            },
            {
                "email": "alumno@agm.com",
                "nombre_completo": "Alumno de Prueba",
                "password": "password123",
                "rol": UserRole.ALUMNO
            }
        ]

        for u in users_to_create:
            existing = user_repo.get_by_email(u["email"])
            if not existing:
                password_hash = pwd_service.hash_password(u["password"])
                user_repo.create(
                    nombre_completo=u["nombre_completo"],
                    email=u["email"],
                    contrasena_hash=password_hash,
                    rol=u["rol"],
                    activo=True,
                )
                print(f"Usuario creado: {u['email']} - Rol: {u['rol']}")
            else:
                print(f"Usuario ya existe: {u['email']}")

        return 0

    except Exception as exc:
        print("Error al ejecutar seed de usuarios de prueba: " + str(exc), file=sys.stderr)
        return 1
    finally:
        db.close()

if __name__ == "__main__":
    raise SystemExit(seed_test_users())
