from pydantic_settings import BaseSettings  # Lee variables de entorno con validación automática


class Settings(BaseSettings):
    """
    Toda la configuración del microservicio viene de variables de entorno.
    Si una variable no existe en el .env, usa el valor por defecto (el que está después del =).
    Pydantic valida automáticamente los tipos — si pones texto donde va un número, lanza error.
    """

    # ── Nombre del microservicio ─────────────────────────────────────────
    # Se usa en los logs y en la documentación automática de FastAPI
    SERVICE_NAME: str = "ms-calificaciones"
    API_V1_PREFIX: str = "/api/v1"  # Todas tus rutas empiezan con esto: /api/v1/ponderaciones, etc.

    # ── Base de datos ────────────────────────────────────────────────────
    # Estos valores deben coincidir exactamente con los del docker-compose.yml
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "db"          # "db" es el nombre del contenedor en docker-compose
    POSTGRES_PORT: int = 5432          # Puerto estándar de PostgreSQL
    POSTGRES_DB: str = "calificaciones_db"

    @property
    def DATABASE_URL(self) -> str:
        """
        Construye la URL de conexión a partir de las variables anteriores.
        SQLAlchemy necesita esta URL para saber a qué BD conectarse.
        Formato: postgresql://usuario:contraseña@host:puerto/nombre_bd
        """
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # ── gRPC ─────────────────────────────────────────────────────────────
    # Puerto donde tu microservicio escucha peticiones gRPC de otros MS
    GRPC_PORT: int = 50054  # Cada MS usa un puerto distinto para no colisionar

    class Config:
        # Le dice a Pydantic que lea las variables desde un archivo .env
        # Si la variable existe en el sistema también la toma (docker la inyecta así)
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instancia única que se importa en todo el proyecto
# En vez de crear Settings() en cada archivo, todos importan este objeto
settings = Settings()