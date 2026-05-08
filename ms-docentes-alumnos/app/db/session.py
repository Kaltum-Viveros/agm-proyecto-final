from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Importamos settings para obtener la DATABASE_URL
from app.core.config import settings

# 1. Creamos el motor (Engine)
# Usamos la URL que definiremos en el .env
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Verifica que la conexión esté viva antes de usarla
)

# 2. Creamos la fábrica de sesiones
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# 3. Dependencia para FastAPI
# Esta función se encargará de abrir y cerrar la conexión en cada petición
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()