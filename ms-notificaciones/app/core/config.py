# Configuración del sistema
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "MS Notificaciones"
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    REST_HOST: str = "0.0.0.0"
    REST_PORT: int = 8005
    
    GRPC_HOST: str = "0.0.0.0"
    GRPC_PORT: int = 50056
    
    CORS_ORIGINS: str = ""
    
    DATABASE_URL: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()