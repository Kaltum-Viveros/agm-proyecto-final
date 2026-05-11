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

    # Ajustes de la base de datos para SQLAlchemy
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/agm_periodos_db",
        alias="DATABASE_URL",
    )
    db_echo: bool = Field(default=True, alias="DB_ECHO")

    GRPC_HOST: str = "0.0.0.0"
    GRPC_PORT: int = 50052

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()

@lru_cache
def get_settings() -> Settings:
    return Settings()





