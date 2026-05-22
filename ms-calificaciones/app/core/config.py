from typing import List
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    service_name: str = "ms-calificaciones"
    env: str = "development"
    cors_allowed_origins: str = "*"

    rest_host: str = "0.0.0.0"
    rest_port: int = 8004

    grpc_host: str = "0.0.0.0"
    grpc_port: int = 50054

    # MS-Auth (MS-1) — para validar tokens JWT
    ms_auth_grpc_host: str = "ms-auth"
    ms_auth_grpc_port: int = 50051

    # MS-Docentes-Alumnos (MS-3) — para verificar inscripciones de alumnos
    ms_docentes_alumnos_grpc_host: str = "ms-docentes-alumnos"
    ms_docentes_alumnos_grpc_port: int = 50053

    # MS-Notificaciones (MS-6) — para el cierre de actas
    ms_notificaciones_grpc_host: str = "ms-notificaciones"
    ms_notificaciones_grpc_port: int = 50056


    # Legacy (mantener por compatibilidad interna)
    ms_alumnos_grpc_url: str = "ms-docentes-alumnos:50053"

    database_url: str = "not_configured_yet"

    # memory | database
    storage_mode: str = "memory"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode='after')
    def validate_database_url(self) -> 'Settings':
        if self.storage_mode == "database" and (not self.database_url or self.database_url == "not_configured_yet"):
            raise ValueError("DATABASE_URL is required when STORAGE_MODE is 'database'")
        return self

    @property
    def cors_origins_list(self) -> List[str]:
        if not self.cors_allowed_origins:
            return []
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]


settings = Settings()