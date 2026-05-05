from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Importar modelos aqui permite que SQLAlchemy y Alembic detecten las tablas.
# Estos imports se usaran mas adelante al configurar migraciones.
from app.models.user import User  # noqa: E402,F401
from app.models.auth_token import AuthToken  # noqa: E402,F401