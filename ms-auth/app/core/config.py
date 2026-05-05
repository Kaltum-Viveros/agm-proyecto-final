from typing import List

from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "MS Auth & Users"
    app_env: str = "development"
    debug: bool = True

    rest_host: str = "0.0.0.0"
    rest_port: int = 8001

    grpc_host: str = "0.0.0.0"
    grpc_port: int = 50051

    cors_origins: str = "http://localhost:4200,http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = False

    def get_cors_origins(self) -> List[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


settings = Settings()