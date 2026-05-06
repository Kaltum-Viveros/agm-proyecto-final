from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "ms-asistencias"
    ENVIRONMENT: str = "local"

    REST_HOST: str = "0.0.0.0"
    REST_PORT: int = 8005

    GRPC_HOST: str = "0.0.0.0"
    GRPC_PORT: int = 50055

    DATABASE_URL: str

    QR_SECRET_KEY: str
    QR_TTL_SECONDS: int = 20
    SESSION_DURATION_MINUTES: int = 10
    PRESENT_LIMIT_MINUTES: int = 5

    AUTH_GRPC_HOST: str = "ms-auth"
    AUTH_GRPC_PORT: int = 50051

    MATERIAS_GRPC_HOST: str = "ms-periodos"
    MATERIAS_GRPC_PORT: int = 50052

    ALUMNOS_GRPC_HOST: str = "ms-alumnos"
    ALUMNOS_GRPC_PORT: int = 50053

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
