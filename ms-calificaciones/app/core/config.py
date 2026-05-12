from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "ms-calificaciones"
    env: str = "development"

    rest_host: str = "0.0.0.0"
    rest_port: int = 8004

    grpc_host: str = "0.0.0.0"
    grpc_port: int = 50054

    # URL del MS-3 para cliente gRPC
    ms_alumnos_grpc_url: str = "localhost:50053"

    database_url: str = "not_configured_yet"

    # memory | database
    storage_mode: str = "memory"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()