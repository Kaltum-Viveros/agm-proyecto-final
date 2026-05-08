from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MS Auth & Users"
    app_env: str = "development"
    debug: bool = True

    rest_host: str = "0.0.0.0"
    rest_port: int = 8001

    grpc_host: str = "0.0.0.0"
    grpc_port: int = 50051

    cors_origins: str = "http://localhost:4200,http://localhost:3000"

    database_url: str = (
        "postgresql://agm_auth_user:agm_auth_password@localhost:5432/agm_auth_db"
    )

    jwt_secret_key: str = "change-this-secret-key-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    password_reset_token_expire_minutes: int = 15

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )

    def get_cors_origins(self) -> List[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


settings = Settings()