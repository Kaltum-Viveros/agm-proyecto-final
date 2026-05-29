from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = Field(default="ms-periodos-materias", alias="SERVICE_NAME")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=True, alias="DEBUG")

    rest_host: str = Field(default="127.0.0.1", alias="REST_HOST")
    rest_port: int = Field(default=8002, alias="REST_PORT")

    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")

    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/agm_periodos_db",
        alias="DATABASE_URL",
    )
    db_echo: bool = Field(default=True, alias="DB_ECHO")

    grpc_host: str = Field(default="0.0.0.0", alias="GRPC_HOST")
    grpc_port: int = Field(default=50052, alias="GRPC_PORT")

    cors_allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173,http://localhost:8000,http://localhost:4200,https://agm-frontend-cdcd.onrender.com",
        alias="CORS_ALLOWED_ORIGINS",
    )

    ms_auth_grpc_host: str = Field(default="ms-auth-api", alias="MS_AUTH_GRPC_HOST")
    ms_auth_grpc_port: int = Field(default=50051, alias="MS_AUTH_GRPC_PORT")

    ms_docentes_alumnos_grpc_host: str = Field(
        default="ms-docentes-alumnos-api",
        alias="MS_DOCENTES_ALUMNOS_GRPC_HOST",
    )
    ms_docentes_alumnos_grpc_port: int = Field(
        default=50053,
        alias="MS_DOCENTES_ALUMNOS_GRPC_PORT",
    )

    model_config = SettingsConfigDict(
    env_file_encoding="utf-8",
    extra="ignore",
)

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_allowed_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()