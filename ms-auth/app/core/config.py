from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MS Auth"
    app_env: str = "development"
    debug: bool = True

    api_host: str = "0.0.0.0"
    api_port: int = 8001

    grpc_host: str = "0.0.0.0"
    grpc_port: int = 50051

    cors_origins: str = (
        "http://localhost:3000,"
        "http://localhost:4200,"
        "http://localhost:5173,"
        "http://localhost:8001"
    )

    database_url: str = (
        "postgresql://agm_auth_user:agm_auth_password@localhost:5432/agm_auth_db"
    )

    jwt_secret_key: str = "change-this-secret-key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    password_reset_token_expire_minutes: int = 15

    seed_admin_name: str = "Administrador AGM"
    seed_admin_email: str = "admin@agm.com"
    seed_admin_password: str = "Admin12345"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def get_cors_origins(self) -> List[str]:
        if not self.cors_origins:
            return []

        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()