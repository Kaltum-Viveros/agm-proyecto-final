# Configuración del sistema
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class settings(BaseSettings):
    APP_NAME: str = "MS Notificaciones"
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    REST_HOST: str = "0.0.0.0"
    REST_PORT: int = 8005
    
    GRPC_HOST: str = "0.0.0.0"
    GRPC_PORT: int = 50056
    
    CORS_ORIGINS: str = ""
    
    DATABASE_URL: str
    
    # SMTP Config
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    # MS-Auth (MS-1)
    ms_auth_grpc_host: str = "ms-auth"
    ms_auth_grpc_port: int = 50051

    # MS-Periodos-Materias (MS-2)
    ms_periodos_materias_grpc_host: str = "ms-periodos-materias"
    ms_periodos_materias_grpc_port: int = 50052

    # MS-Docentes-Alumnos (MS-3)
    ms_docentes_alumnos_grpc_host: str = "ms-docentes-alumnos"
    ms_docentes_alumnos_grpc_port: int = 50053


    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

@lru_cache()
def get_settings() -> settings:
    return settings()

settings = get_settings()