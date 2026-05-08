from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Información General del Microservicio
    app_name: str = "MS Docentes y Alumnos"
    app_env: str = "development"
    debug: bool = True

    # Configuración de Red (REST y gRPC)
    rest_host: str = "0.0.0.0"
    rest_port: int = 8003  # Usamos el 8003 para no chocar con Auth (8001) ni otros
    
    grpc_host: str = "0.0.0.0"
    grpc_port: int = 50053 # Puerto gRPC sugerido para este MS

    # Base de Datos
    # Esta es la variable que busca session.py
    # El valor por defecto es para tu entorno local de desarrollo
    database_url: str = "postgresql://tu_usuario:tu_password@localhost:5432/agm_docentes_alumnos_db"

    # Configuración para leer el archivo .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()