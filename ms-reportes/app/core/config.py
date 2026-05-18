from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SERVICE_NAME: str = "ms-reportes"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    REST_HOST: str = "0.0.0.0"
    REST_PORT: int = 8007

    GRPC_HOST: str = "0.0.0.0"
    GRPC_PORT: int = 50057

    DATABASE_URL: str

    API_V1_PREFIX: str = "/api/v1"

    # MS-Auth (MS-1) — para validar tokens JWT
    AUTH_GRPC_HOST: str = "ms-auth"
    AUTH_GRPC_PORT: int = 50051

    # MS-Periodos-Materias (MS-2)
    MATERIAS_GRPC_HOST: str = "ms-periodos-materias"
    MATERIAS_GRPC_PORT: int = 50052

    # MS-Docentes-Alumnos (MS-3)
    ALUMNOS_GRPC_HOST: str = "ms-docentes-alumnos"
    ALUMNOS_GRPC_PORT: int = 50053

    # MS-Calificaciones (MS-4)
    CALIFICACIONES_GRPC_HOST: str = "ms-calificaciones"
    CALIFICACIONES_GRPC_PORT: int = 50054

    # MS-Asistencias (MS-5)
    ASISTENCIAS_GRPC_HOST: str = "ms-asistencias"
    ASISTENCIAS_GRPC_PORT: int = 50055

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
